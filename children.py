from flask import Blueprint, request, jsonify, current_app
from src.models.user import db, User, Child
from src.routes.auth import token_required, admin_required
from datetime import datetime
import uuid

children_bp = Blueprint('children', __name__)

@children_bp.route('/add', methods=['POST'])
@token_required
def add_child(current_user):
    """إضافة طفل جديد (ولي الأمر فقط)"""
    try:
        # التحقق من أن المستخدم هو ولي أمر
        if current_user.role != 'parent':
            return jsonify({'message': 'Only parents can add children'}), 403
        
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        if not data.get('name'):
            return jsonify({'message': 'Child name is required'}), 400
        
        # إنشاء الطفل الجديد
        child = Child(
            name=data['name'],
            birthdate=datetime.strptime(data['birthdate'], '%Y-%m-%d').date() if data.get('birthdate') else None,
            parent_id=current_user.id,
            photo_url=data.get('photo_url'),
            is_approved=False  # يحتاج موافقة الإدارة
        )
        
        db.session.add(child)
        db.session.flush()  # للحصول على ID الطفل
        
        # توليد QR Code
        child.generate_qr_code()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Child added successfully. Waiting for admin approval.',
            'child': child.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to add child: {str(e)}'}), 500

@children_bp.route('/my-children', methods=['GET'])
@token_required
def get_my_children(current_user):
    """الحصول على قائمة أطفال ولي الأمر"""
    try:
        if current_user.role != 'parent':
            return jsonify({'message': 'Only parents can view their children'}), 403
        
        children = Child.query.filter_by(parent_id=current_user.id, is_active=True).all()
        
        return jsonify({
            'children': [child.to_dict() for child in children]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get children: {str(e)}'}), 500

@children_bp.route('/pending-approval', methods=['GET'])
@token_required
@admin_required
def get_pending_children(current_user):
    """الحصول على قائمة الأطفال المنتظرين الموافقة (الإدارة فقط)"""
    try:
        children = Child.query.filter_by(is_approved=False, is_active=True).all()
        
        children_with_parents = []
        for child in children:
            child_dict = child.to_dict()
            child_dict['parent'] = child.parent.to_dict()
            children_with_parents.append(child_dict)
        
        return jsonify({
            'pending_children': children_with_parents
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get pending children: {str(e)}'}), 500

@children_bp.route('/<int:child_id>/approve', methods=['POST'])
@token_required
@admin_required
def approve_child(current_user, child_id):
    """الموافقة على طفل (الإدارة فقط)"""
    try:
        child = Child.query.get(child_id)
        
        if not child:
            return jsonify({'message': 'Child not found'}), 404
        
        child.is_approved = True
        child.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Child approved successfully',
            'child': child.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to approve child: {str(e)}'}), 500

@children_bp.route('/<int:child_id>/reject', methods=['POST'])
@token_required
@admin_required
def reject_child(current_user, child_id):
    """رفض طفل (الإدارة فقط)"""
    try:
        child = Child.query.get(child_id)
        
        if not child:
            return jsonify({'message': 'Child not found'}), 404
        
        data = request.get_json()
        rejection_reason = data.get('reason', 'No reason provided')
        
        # يمكن إضافة حقل لسبب الرفض في المستقبل
        child.is_active = False
        child.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Child rejected successfully',
            'reason': rejection_reason
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to reject child: {str(e)}'}), 500

@children_bp.route('/all', methods=['GET'])
@token_required
@admin_required
def get_all_children(current_user):
    """الحصول على قائمة جميع الأطفال (الإدارة فقط)"""
    try:
        children = Child.query.filter_by(is_active=True).all()
        
        children_with_parents = []
        for child in children:
            child_dict = child.to_dict()
            child_dict['parent'] = child.parent.to_dict()
            children_with_parents.append(child_dict)
        
        return jsonify({
            'children': children_with_parents
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get children: {str(e)}'}), 500

@children_bp.route('/<int:child_id>', methods=['GET'])
@token_required
def get_child_details(current_user, child_id):
    """الحصول على تفاصيل طفل محدد"""
    try:
        child = Child.query.get(child_id)
        
        if not child:
            return jsonify({'message': 'Child not found'}), 404
        
        # التحقق من الصلاحيات
        if current_user.role == 'parent' and child.parent_id != current_user.id:
            return jsonify({'message': 'Access denied'}), 403
        
        child_dict = child.to_dict()
        
        # إضافة بيانات ولي الأمر للإدارة والموظفين
        if current_user.role in ['admin', 'staff']:
            child_dict['parent'] = child.parent.to_dict()
        
        return jsonify({
            'child': child_dict
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get child details: {str(e)}'}), 500

@children_bp.route('/<int:child_id>', methods=['PUT'])
@token_required
def update_child(current_user, child_id):
    """تحديث بيانات طفل"""
    try:
        child = Child.query.get(child_id)
        
        if not child:
            return jsonify({'message': 'Child not found'}), 404
        
        # التحقق من الصلاحيات
        if current_user.role == 'parent' and child.parent_id != current_user.id:
            return jsonify({'message': 'Access denied'}), 403
        elif current_user.role == 'staff':
            return jsonify({'message': 'Staff cannot edit child information'}), 403
        
        data = request.get_json()
        
        # تحديث البيانات المسموحة
        if data.get('name'):
            child.name = data['name']
        if data.get('birthdate'):
            child.birthdate = datetime.strptime(data['birthdate'], '%Y-%m-%d').date()
        if data.get('photo_url'):
            child.photo_url = data['photo_url']
        
        child.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Child updated successfully',
            'child': child.to_dict()
        }), 200
        
    except ValueError as e:
        return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to update child: {str(e)}'}), 500

@children_bp.route('/<int:child_id>/qr-code', methods=['GET'])
@token_required
def get_child_qr_code(current_user, child_id):
    """الحصول على QR Code الخاص بالطفل"""
    try:
        child = Child.query.get(child_id)
        
        if not child:
            return jsonify({'message': 'Child not found'}), 404
        
        # التحقق من الصلاحيات
        if current_user.role == 'parent' and child.parent_id != current_user.id:
            return jsonify({'message': 'Access denied'}), 403
        
        if not child.is_approved:
            return jsonify({'message': 'Child is not approved yet'}), 400
        
        return jsonify({
            'child_id': child.id,
            'child_name': child.name,
            'qr_code': child.qr_code
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get QR code: {str(e)}'}), 500

