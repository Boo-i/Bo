from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import uuid

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('admin', 'staff', 'parent', name='user_roles'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(255), nullable=True)
    reset_token = db.Column(db.String(255), nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    children = db.relationship('Child', backref='parent', lazy=True, foreign_keys='Child.parent_id')
    staff_updates = db.relationship('DailyUpdate', backref='staff_member', lazy=True, foreign_keys='DailyUpdate.staff_id')
    attendance_records = db.relationship('Attendance', backref='staff_member', lazy=True, foreign_keys='Attendance.staff_id')
    
    def set_password(self, password):
        """تشفير كلمة المرور"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """التحقق من كلمة المرور"""
        return check_password_hash(self.password_hash, password)
    
    def generate_verification_token(self):
        """توليد رمز التحقق"""
        self.verification_token = str(uuid.uuid4())
        return self.verification_token
    
    def generate_reset_token(self):
        """توليد رمز إعادة تعيين كلمة المرور"""
        self.reset_token = str(uuid.uuid4())
        self.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        return self.reset_token
    
    def to_dict(self):
        """تحويل البيانات إلى قاموس"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Child(db.Model):
    __tablename__ = 'children'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    birthdate = db.Column(db.Date, nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    qr_code = db.Column(db.String(255), unique=True, nullable=True)
    photo_url = db.Column(db.String(255), nullable=True)
    is_approved = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    attendance_records = db.relationship('Attendance', backref='child', lazy=True)
    daily_updates = db.relationship('DailyUpdate', backref='child', lazy=True)
    
    def generate_qr_code(self):
        """توليد QR Code للطفل"""
        self.qr_code = f"CHILD_{self.id}_{str(uuid.uuid4())[:8]}"
        return self.qr_code
    
    def to_dict(self):
        """تحويل البيانات إلى قاموس"""
        return {
            'id': self.id,
            'name': self.name,
            'birthdate': self.birthdate.isoformat() if self.birthdate else None,
            'parent_id': self.parent_id,
            'qr_code': self.qr_code,
            'photo_url': self.photo_url,
            'is_approved': self.is_approved,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('children.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.Enum('check_in', 'check_out', name='attendance_status'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        """تحويل البيانات إلى قاموس"""
        return {
            'id': self.id,
            'child_id': self.child_id,
            'staff_id': self.staff_id,
            'status': self.status,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'notes': self.notes
        }

class DailyUpdate(db.Model):
    __tablename__ = 'daily_updates'
    
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('children.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    note = db.Column(db.Text, nullable=True)
    photo_url = db.Column(db.String(255), nullable=True)
    video_url = db.Column(db.String(255), nullable=True)
    activity_type = db.Column(db.String(50), nullable=True)  # أكل، نوم، لعب، تعلم
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """تحويل البيانات إلى قاموس"""
        return {
            'id': self.id,
            'child_id': self.child_id,
            'staff_id': self.staff_id,
            'note': self.note,
            'photo_url': self.photo_url,
            'video_url': self.video_url,
            'activity_type': self.activity_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

