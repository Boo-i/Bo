from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from src.models.user import db, User, Child
import jwt
from datetime import datetime, timedelta
from functools import wraps
import uuid

auth_bp = Blueprint('auth', __name__)

def token_required(f):
    """Decorator للتحقق من صحة JWT Token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(id=data['user_id']).first()
            
            if not current_user:
                return jsonify({'message': 'Token is invalid!'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator للتحقق من صلاحيات الإدارة"""
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.role != 'admin':
            return jsonify({'message': 'Admin access required!'}), 403
        return f(current_user, *args, **kwargs)
    
    return decorated

@auth_bp.route('/register/parent', methods=['POST'])
def register_parent():
    """تسجيل ولي أمر جديد"""
    try:
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        required_fields = ['name', 'email', 'password', 'phone']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} is required'}), 400
        
        # التحقق من عدم وجود المستخدم مسبقاً
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email already exists'}), 400
        
        # إنشاء المستخدم الجديد
        user = User(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            role='parent'
        )
        user.set_password(data['password'])
        user.generate_verification_token()
        
        db.session.add(user)
        db.session.commit()
        
        # توليد JWT Token
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(days=30)
        }, current_app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'message': 'Parent registered successfully',
            'token': token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/register/staff', methods=['POST'])
def register_staff():
    """تسجيل موظف جديد (يتطلب دعوة من الإدارة)"""
    try:
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        required_fields = ['name', 'email', 'password', 'phone']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} is required'}), 400
        
        # التحقق من كود الدعوة (اختياري - يمكن تطويره لاحقاً)
        invitation_code = data.get('invitation_code')
        
        # التحقق من عدم وجود المستخدم مسبقاً
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email already exists'}), 400
        
        # إنشاء المستخدم الجديد
        user = User(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            role='staff',
            is_verified=True  # الموظفين يتم تفعيلهم مباشرة
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # توليد JWT Token
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(days=30)
        }, current_app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'message': 'Staff registered successfully',
            'token': token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """تسجيل دخول المستخدمين"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Email and password are required'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'message': 'Invalid email or password'}), 401
        
        if not user.is_active:
            return jsonify({'message': 'Account is deactivated'}), 401
        
        # توليد JWT Token
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(days=30)
        }, current_app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Login failed: {str(e)}'}), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """طلب إعادة تعيين كلمة المرور"""
    try:
        data = request.get_json()
        
        if not data.get('email'):
            return jsonify({'message': 'Email is required'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user:
            return jsonify({'message': 'Email not found'}), 404
        
        # توليد رمز إعادة التعيين
        reset_token = user.generate_reset_token()
        db.session.commit()
        
        # هنا يمكن إرسال البريد الإلكتروني أو SMS
        # TODO: إضافة خدمة إرسال البريد الإلكتروني
        
        return jsonify({
            'message': 'Password reset token generated',
            'reset_token': reset_token  # في الإنتاج، لا نرسل الرمز في الاستجابة
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to generate reset token: {str(e)}'}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """إعادة تعيين كلمة المرور"""
    try:
        data = request.get_json()
        
        required_fields = ['reset_token', 'new_password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} is required'}), 400
        
        user = User.query.filter_by(reset_token=data['reset_token']).first()
        
        if not user:
            return jsonify({'message': 'Invalid reset token'}), 400
        
        if user.reset_token_expires and user.reset_token_expires < datetime.utcnow():
            return jsonify({'message': 'Reset token has expired'}), 400
        
        # تحديث كلمة المرور
        user.set_password(data['new_password'])
        user.reset_token = None
        user.reset_token_expires = None
        
        db.session.commit()
        
        return jsonify({'message': 'Password reset successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Password reset failed: {str(e)}'}), 500

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """الحصول على بيانات المستخدم الحالي"""
    return jsonify({
        'user': current_user.to_dict()
    }), 200

@auth_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """تحديث بيانات المستخدم الحالي"""
    try:
        data = request.get_json()
        
        # تحديث البيانات المسموحة
        if data.get('name'):
            current_user.name = data['name']
        if data.get('phone'):
            current_user.phone = data['phone']
        
        current_user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': current_user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Profile update failed: {str(e)}'}), 500

