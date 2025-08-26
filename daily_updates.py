from flask import Blueprint, request, jsonify, current_app
from src.models.user import db, User, Child, DailyUpdate
from src.routes.auth import token_required, admin_required
from datetime import datetime, date
from sqlalchemy import and_, func

daily_updates_bp = Blueprint('daily_updates', __name__)

@daily_updates_bp.route('/add', methods=['POST'])
@token_required
def add_daily_update(current_user):
    """إضافة تحديث يومي (الموظفين والإدارة فقط)"""
    try:
        if current_user.role not in ['staff', 'admin']:
            return jsonify({'message': 'Only staff can add daily updates'}), 403
        
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        if not data.get('child_id'):
            return jsonify({'message': 'Child ID is required'}), 400
        
        child = Child.query.get(data['child_id'])
        
        if not child:
            return jsonify({'message': 'Child not found'}), 404
        
        if not child.is_approved:
            return jsonify({'message': 'Child is not approved yet'}), 400
        
        # إنشاء التحديث اليومي
        daily_update = DailyUpdate(
            child_id=data['child_id'],
            staff_id=current_user.id,
            note=data.get('note'),
            photo_url=data.get('photo_url'),
            video_url=data.get('video_url'),
            activity_type=data.get('activity_type')  # أكل، نوم، لعب، تعلم
        )
        
        db.session.add(daily_update)
        db.session.commit()
        
        # إرسال إشعار لولي الأمر (TODO: تنفيذ الإشعارات)
        
        return jsonify({
            'message': 'Daily update added successfully',
            'update': daily_update.to_dict(),
            'child': child.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to add daily update: {str(e)}'}), 500

@daily_updates_bp.route('/child/<int:child_id>/today', methods=['GET'])
@token_required
def get_child_updates_today(current_user, child_id):
    """الحصول على تحديثات طفل محدد لليوم الحالي"""
    try:
        child = Child.query.get(child_id)
        
        if not child:
            return jsonify({'message': 'Child not found'}), 404
        
        # التحقق من الصلاحيات
        if current_user.role == 'parent' and child.parent_id != current_user.id:
            return jsonify({'message': 'Access denied'}), 403
        
        # الحصول على تحديثات اليوم
        today = date.today()
        updates = DailyUpdate.query.filter(
            and_(
                DailyUpdate.child_id == child_id,
                func.date(DailyUpdate.created_at) == today
            )
        ).order_by(DailyUpdate.created_at.desc()).all()
        
        # إضافة معلومات الموظف لكل تحديث
        updates_with_staff = []
        for update in updates:
            update_dict = update.to_dict()
            update_dict['staff'] = update.staff_member.to_dict()
            updates_with_staff.append(update_dict)
        
        return jsonify({
            'child': child.to_dict(),
            'date': today.isoformat(),
            'updates': updates_with_staff
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get daily updates: {str(e)}'}), 500

@daily_updates_bp.route('/child/<int:child_id>/history', methods=['GET'])
@token_required
def get_child_updates_history(current_user, child_id):
    """الحصول على تاريخ تحديثات طفل محدد"""
    try:
        child = Child.query.get(child_id)
        
        if not child:
            return jsonify({'message': 'Child not found'}), 404
        
        # التحقق من الصلاحيات
        if current_user.role == 'parent' and child.parent_id != current_user.id:
            return jsonify({'message': 'Access denied'}), 403
        
        # الحصول على معاملات الاستعلام
        days = request.args.get('days', 7, type=int)  # آخر 7 أيام افتراضياً
        activity_type = request.args.get('activity_type')  # تصفية حسب نوع النشاط
        
        # بناء الاستعلام
        query = DailyUpdate.query.filter_by(child_id=child_id)
        
        if activity_type:
            query = query.filter_by(activity_type=activity_type)
        
        # الحصول على التحديثات
        updates = query.order_by(DailyUpdate.created_at.desc())\
            .limit(days * 10).all()  # تقدير 10 تحديثات كحد أقصى في اليوم
        
        # تجميع البيانات حسب التاريخ
        daily_updates = {}
        
        for update in updates:
            update_date = update.created_at.date().isoformat()
            
            if update_date not in daily_updates:
                daily_updates[update_date] = {
                    'date': update_date,
                    'updates': []
                }
            
            update_dict = update.to_dict()
            update_dict['staff'] = update.staff_member.to_dict()
            daily_updates[update_date]['updates'].append(update_dict)
        
        # ترتيب البيانات حسب التاريخ
        sorted_updates = sorted(daily_updates.values(), 
                              key=lambda x: x['date'], reverse=True)
        
        return jsonify({
            'child': child.to_dict(),
            'updates_history': sorted_updates
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get updates history: {str(e)}'}), 500

@daily_updates_bp.route('/my-children/today', methods=['GET'])
@token_required
def get_my_children_updates_today(current_user):
    """الحصول على تحديثات جميع أطفال ولي الأمر لليوم الحالي"""
    try:
        if current_user.role != 'parent':
            return jsonify({'message': 'Only parents can view their children updates'}), 403
        
        # الحصول على أطفال ولي الأمر
        children = Child.query.filter_by(
            parent_id=current_user.id, 
            is_approved=True, 
            is_active=True
        ).all()
        
        today = date.today()
        children_updates = []
        
        for child in children:
            # الحصول على تحديثات اليوم لهذا الطفل
            updates = DailyUpdate.query.filter(
                and_(
                    DailyUpdate.child_id == child.id,
                    func.date(DailyUpdate.created_at) == today
                )
            ).order_by(DailyUpdate.created_at.desc()).all()
            
            # إضافة معلومات الموظف لكل تحديث
            updates_with_staff = []
            for update in updates:
                update_dict = update.to_dict()
                update_dict['staff'] = update.staff_member.to_dict()
                updates_with_staff.append(update_dict)
            
            children_updates.append({
                'child': child.to_dict(),
                'updates': updates_with_staff,
                'updates_count': len(updates_with_staff)
            })
        
        return jsonify({
            'date': today.isoformat(),
            'children_updates': children_updates
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get children updates: {str(e)}'}), 500

@daily_updates_bp.route('/today', methods=['GET'])
@token_required
def get_all_updates_today(current_user):
    """الحصول على جميع التحديثات اليومية (الموظفين والإدارة)"""
    try:
        if current_user.role not in ['staff', 'admin']:
            return jsonify({'message': 'Access denied'}), 403
        
        today = date.today()
        
        # الحصول على جميع التحديثات اليوم
        updates = DailyUpdate.query.filter(
            func.date(DailyUpdate.created_at) == today
        ).order_by(DailyUpdate.created_at.desc()).all()
        
        # إضافة معلومات الطفل والموظف لكل تحديث
        updates_with_details = []
        for update in updates:
            update_dict = update.to_dict()
            update_dict['child'] = update.child.to_dict()
            update_dict['staff'] = update.staff_member.to_dict()
            updates_with_details.append(update_dict)
        
        # إحصائيات سريعة
        total_updates = len(updates_with_details)
        activity_types = {}
        
        for update in updates_with_details:
            activity_type = update.get('activity_type', 'غير محدد')
            activity_types[activity_type] = activity_types.get(activity_type, 0) + 1
        
        return jsonify({
            'date': today.isoformat(),
            'summary': {
                'total_updates': total_updates,
                'activity_breakdown': activity_types
            },
            'updates': updates_with_details
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get today updates: {str(e)}'}), 500

@daily_updates_bp.route('/<int:update_id>', methods=['PUT'])
@token_required
def update_daily_update(current_user, update_id):
    """تحديث تحديث يومي (الموظف الذي أنشأه أو الإدارة فقط)"""
    try:
        daily_update = DailyUpdate.query.get(update_id)
        
        if not daily_update:
            return jsonify({'message': 'Update not found'}), 404
        
        # التحقق من الصلاحيات
        if current_user.role == 'staff' and daily_update.staff_id != current_user.id:
            return jsonify({'message': 'You can only edit your own updates'}), 403
        elif current_user.role not in ['staff', 'admin']:
            return jsonify({'message': 'Access denied'}), 403
        
        data = request.get_json()
        
        # تحديث البيانات المسموحة
        if data.get('note') is not None:
            daily_update.note = data['note']
        if data.get('photo_url') is not None:
            daily_update.photo_url = data['photo_url']
        if data.get('video_url') is not None:
            daily_update.video_url = data['video_url']
        if data.get('activity_type') is not None:
            daily_update.activity_type = data['activity_type']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Daily update updated successfully',
            'update': daily_update.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to update daily update: {str(e)}'}), 500

@daily_updates_bp.route('/<int:update_id>', methods=['DELETE'])
@token_required
def delete_daily_update(current_user, update_id):
    """حذف تحديث يومي (الموظف الذي أنشأه أو الإدارة فقط)"""
    try:
        daily_update = DailyUpdate.query.get(update_id)
        
        if not daily_update:
            return jsonify({'message': 'Update not found'}), 404
        
        # التحقق من الصلاحيات
        if current_user.role == 'staff' and daily_update.staff_id != current_user.id:
            return jsonify({'message': 'You can only delete your own updates'}), 403
        elif current_user.role not in ['staff', 'admin']:
            return jsonify({'message': 'Access denied'}), 403
        
        db.session.delete(daily_update)
        db.session.commit()
        
        return jsonify({
            'message': 'Daily update deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to delete daily update: {str(e)}'}), 500

@daily_updates_bp.route('/activity-types', methods=['GET'])
@token_required
def get_activity_types(current_user):
    """الحصول على قائمة أنواع الأنشطة المتاحة"""
    activity_types = [
        {'value': 'أكل', 'label': 'وجبة طعام', 'icon': '🍽️'},
        {'value': 'نوم', 'label': 'وقت النوم', 'icon': '😴'},
        {'value': 'لعب', 'label': 'وقت اللعب', 'icon': '🎮'},
        {'value': 'تعلم', 'label': 'نشاط تعليمي', 'icon': '📚'},
        {'value': 'رياضة', 'label': 'نشاط رياضي', 'icon': '⚽'},
        {'value': 'فن', 'label': 'نشاط فني', 'icon': '🎨'},
        {'value': 'موسيقى', 'label': 'نشاط موسيقي', 'icon': '🎵'},
        {'value': 'طبي', 'label': 'رعاية طبية', 'icon': '🏥'},
        {'value': 'أخرى', 'label': 'أنشطة أخرى', 'icon': '📝'}
    ]
    
    return jsonify({
        'activity_types': activity_types
    }), 200

