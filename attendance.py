from flask import Blueprint, request, jsonify, current_app
from src.models.user import db, User, Child, Attendance
from src.routes.auth import token_required, admin_required
from datetime import datetime, date
from sqlalchemy import and_, func

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/scan-qr', methods=['POST'])
@token_required
def scan_qr_code(current_user):
    """مسح QR Code للحضور والانصراف (الموظفين فقط)"""
    try:
        # التحقق من أن المستخدم موظف
        if current_user.role not in ['staff', 'admin']:
            return jsonify({'message': 'Only staff can scan QR codes'}), 403
        
        data = request.get_json()
        qr_code = data.get('qr_code')
        
        if not qr_code:
            return jsonify({'message': 'QR code is required'}), 400
        
        # البحث عن الطفل بواسطة QR Code
        child = Child.query.filter_by(qr_code=qr_code, is_approved=True, is_active=True).first()
        
        if not child:
            return jsonify({'message': 'Invalid QR code or child not approved'}), 404
        
        # التحقق من آخر حالة حضور للطفل اليوم
        today = date.today()
        last_attendance = Attendance.query.filter(
            and_(
                Attendance.child_id == child.id,
                func.date(Attendance.timestamp) == today
            )
        ).order_by(Attendance.timestamp.desc()).first()
        
        # تحديد نوع العملية (دخول أم خروج)
        if not last_attendance or last_attendance.status == 'check_out':
            # الطفل غير موجود أو خرج، فهذا دخول
            status = 'check_in'
            message = f'{child.name} تم تسجيل دخوله بنجاح'
        else:
            # الطفل موجود، فهذا خروج
            status = 'check_out'
            message = f'{child.name} تم تسجيل خروجه بنجاح'
        
        # إنشاء سجل حضور جديد
        attendance = Attendance(
            child_id=child.id,
            staff_id=current_user.id,
            status=status,
            notes=data.get('notes')
        )
        
        db.session.add(attendance)
        db.session.commit()
        
        # إرسال إشعار لولي الأمر (TODO: تنفيذ الإشعارات)
        
        return jsonify({
            'message': message,
            'attendance': attendance.to_dict(),
            'child': child.to_dict(),
            'status': status
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to process QR scan: {str(e)}'}), 500

@attendance_bp.route('/child/<int:child_id>/today', methods=['GET'])
@token_required
def get_child_attendance_today(current_user, child_id):
    """الحصول على حضور طفل محدد لليوم الحالي"""
    try:
        child = Child.query.get(child_id)
        
        if not child:
            return jsonify({'message': 'Child not found'}), 404
        
        # التحقق من الصلاحيات
        if current_user.role == 'parent' and child.parent_id != current_user.id:
            return jsonify({'message': 'Access denied'}), 403
        
        # الحصول على حضور اليوم
        today = date.today()
        attendance_records = Attendance.query.filter(
            and_(
                Attendance.child_id == child_id,
                func.date(Attendance.timestamp) == today
            )
        ).order_by(Attendance.timestamp.asc()).all()
        
        # تحديد الحالة الحالية
        current_status = 'absent'
        if attendance_records:
            last_record = attendance_records[-1]
            current_status = 'present' if last_record.status == 'check_in' else 'absent'
        
        return jsonify({
            'child': child.to_dict(),
            'current_status': current_status,
            'attendance_records': [record.to_dict() for record in attendance_records]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get attendance: {str(e)}'}), 500

@attendance_bp.route('/today', methods=['GET'])
@token_required
def get_today_attendance(current_user):
    """الحصول على حضور جميع الأطفال لليوم الحالي (الموظفين والإدارة)"""
    try:
        if current_user.role not in ['staff', 'admin']:
            return jsonify({'message': 'Access denied'}), 403
        
        today = date.today()
        
        # الحصول على جميع الأطفال المعتمدين
        children = Child.query.filter_by(is_approved=True, is_active=True).all()
        
        attendance_summary = []
        
        for child in children:
            # الحصول على آخر سجل حضور لهذا الطفل اليوم
            last_attendance = Attendance.query.filter(
                and_(
                    Attendance.child_id == child.id,
                    func.date(Attendance.timestamp) == today
                )
            ).order_by(Attendance.timestamp.desc()).first()
            
            status = 'absent'
            last_action_time = None
            
            if last_attendance:
                status = 'present' if last_attendance.status == 'check_in' else 'absent'
                last_action_time = last_attendance.timestamp.isoformat()
            
            child_data = child.to_dict()
            child_data['parent'] = child.parent.to_dict()
            child_data['current_status'] = status
            child_data['last_action_time'] = last_action_time
            
            attendance_summary.append(child_data)
        
        # إحصائيات سريعة
        present_count = sum(1 for child in attendance_summary if child['current_status'] == 'present')
        absent_count = len(attendance_summary) - present_count
        
        return jsonify({
            'date': today.isoformat(),
            'summary': {
                'total_children': len(attendance_summary),
                'present': present_count,
                'absent': absent_count
            },
            'children': attendance_summary
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get today attendance: {str(e)}'}), 500

@attendance_bp.route('/child/<int:child_id>/history', methods=['GET'])
@token_required
def get_child_attendance_history(current_user, child_id):
    """الحصول على تاريخ حضور طفل محدد"""
    try:
        child = Child.query.get(child_id)
        
        if not child:
            return jsonify({'message': 'Child not found'}), 404
        
        # التحقق من الصلاحيات
        if current_user.role == 'parent' and child.parent_id != current_user.id:
            return jsonify({'message': 'Access denied'}), 403
        
        # الحصول على معاملات الاستعلام
        days = request.args.get('days', 30, type=int)  # آخر 30 يوم افتراضياً
        
        # الحصول على سجلات الحضور
        attendance_records = Attendance.query.filter_by(child_id=child_id)\
            .order_by(Attendance.timestamp.desc())\
            .limit(days * 4).all()  # تقدير 4 سجلات كحد أقصى في اليوم
        
        # تجميع البيانات حسب التاريخ
        daily_attendance = {}
        
        for record in attendance_records:
            record_date = record.timestamp.date().isoformat()
            
            if record_date not in daily_attendance:
                daily_attendance[record_date] = {
                    'date': record_date,
                    'records': [],
                    'status': 'absent'
                }
            
            daily_attendance[record_date]['records'].append(record.to_dict())
            
            # تحديد الحالة النهائية لليوم
            if record.status == 'check_in':
                daily_attendance[record_date]['status'] = 'present'
        
        # ترتيب البيانات حسب التاريخ
        sorted_attendance = sorted(daily_attendance.values(), 
                                 key=lambda x: x['date'], reverse=True)
        
        return jsonify({
            'child': child.to_dict(),
            'attendance_history': sorted_attendance
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get attendance history: {str(e)}'}), 500

@attendance_bp.route('/stats', methods=['GET'])
@token_required
@admin_required
def get_attendance_stats(current_user):
    """الحصول على إحصائيات الحضور (الإدارة فقط)"""
    try:
        # الحصول على معاملات الاستعلام
        days = request.args.get('days', 7, type=int)  # آخر 7 أيام افتراضياً
        
        # حساب التواريخ
        end_date = date.today()
        start_date = date.fromordinal(end_date.toordinal() - days + 1)
        
        # الحصول على جميع الأطفال المعتمدين
        total_children = Child.query.filter_by(is_approved=True, is_active=True).count()
        
        # إحصائيات يومية
        daily_stats = []
        
        for i in range(days):
            current_date = date.fromordinal(start_date.toordinal() + i)
            
            # عدد الأطفال الحاضرين في هذا اليوم
            present_children = db.session.query(Attendance.child_id)\
                .filter(
                    and_(
                        func.date(Attendance.timestamp) == current_date,
                        Attendance.status == 'check_in'
                    )
                ).distinct().count()
            
            daily_stats.append({
                'date': current_date.isoformat(),
                'total_children': total_children,
                'present': present_children,
                'absent': total_children - present_children,
                'attendance_rate': round((present_children / total_children * 100) if total_children > 0 else 0, 2)
            })
        
        # إحصائيات عامة
        avg_attendance_rate = sum(day['attendance_rate'] for day in daily_stats) / len(daily_stats) if daily_stats else 0
        
        return jsonify({
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            },
            'summary': {
                'total_children': total_children,
                'average_attendance_rate': round(avg_attendance_rate, 2)
            },
            'daily_stats': daily_stats
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get attendance stats: {str(e)}'}), 500

