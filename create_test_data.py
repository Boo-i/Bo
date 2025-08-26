#!/usr/bin/env python3
"""
سكريبت لإنشاء بيانات تجريبية لمنصة حاضِن
"""

import sqlite3
import hashlib
import uuid
from datetime import datetime, timedelta
import random

def hash_password(password):
    """تشفير كلمة المرور"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_qr_code():
    """توليد رمز QR فريد"""
    return f"QR_{uuid.uuid4().hex[:8].upper()}"

def create_test_data():
    """إنشاء بيانات تجريبية"""
    conn = sqlite3.connect('hadhin.db')
    cursor = conn.cursor()
    
    # إنشاء الجداول
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            password_hash TEXT NOT NULL,
            role TEXT CHECK(role IN ('admin','staff','parent')) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS children (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            birthdate DATE,
            parent_id INTEGER,
            qr_code TEXT UNIQUE,
            is_approved BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES users(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            child_id INTEGER,
            staff_id INTEGER,
            status TEXT CHECK(status IN ('check_in','check_out')),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            FOREIGN KEY (child_id) REFERENCES children(id),
            FOREIGN KEY (staff_id) REFERENCES users(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            child_id INTEGER,
            staff_id INTEGER,
            activity_type TEXT,
            note TEXT,
            photo_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (child_id) REFERENCES children(id),
            FOREIGN KEY (staff_id) REFERENCES users(id)
        )
    ''')
    
    # مسح البيانات الموجودة
    cursor.execute('DELETE FROM daily_updates')
    cursor.execute('DELETE FROM attendance')
    cursor.execute('DELETE FROM children')
    cursor.execute('DELETE FROM users')
    
    # إنشاء مستخدم إداري
    cursor.execute('''
        INSERT INTO users (name, email, phone, password_hash, role)
        VALUES (?, ?, ?, ?, ?)
    ''', ('أحمد المدير', 'admin@brightkids.com', '0501234567', hash_password('admin123'), 'admin'))
    
    # إنشاء موظفين
    staff_data = [
        ('فاطمة المربية', 'fatima@brightkids.com', '0507654321', 'staff123'),
        ('سارة المشرفة', 'sara@brightkids.com', '0509876543', 'staff123'),
        ('محمد المربي', 'mohammed.staff@brightkids.com', '0502468135', 'staff123'),
    ]
    
    staff_ids = []
    for name, email, phone, password in staff_data:
        cursor.execute('''
            INSERT INTO users (name, email, phone, password_hash, role)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, email, phone, hash_password(password), 'staff'))
        staff_ids.append(cursor.lastrowid)
    
    # إنشاء أولياء أمور
    parents_data = [
        ('محمد أحمد', 'mohammed.parent@gmail.com', '0509876543', 'parent123'),
        ('علي حسن', 'ali.hassan@gmail.com', '0507654321', 'parent123'),
        ('خالد يوسف', 'khalid.youssef@gmail.com', '0501357924', 'parent123'),
        ('عبدالله سالم', 'abdullah.salem@gmail.com', '0508642097', 'parent123'),
        ('أحمد عبدالرحمن', 'ahmed.abdulrahman@gmail.com', '0505432109', 'parent123'),
    ]
    
    parent_ids = []
    for name, email, phone, password in parents_data:
        cursor.execute('''
            INSERT INTO users (name, email, phone, password_hash, role)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, email, phone, hash_password(password), 'parent'))
        parent_ids.append(cursor.lastrowid)
    
    # إنشاء أطفال
    children_data = [
        ('أحمد محمد', '2020-05-15', parent_ids[0], True),
        ('فاطمة علي', '2019-08-22', parent_ids[1], True),
        ('يوسف خالد', '2021-03-10', parent_ids[2], True),
        ('مريم عبدالله', '2020-11-05', parent_ids[3], True),
        ('عمر أحمد', '2019-12-18', parent_ids[4], True),
        ('نور محمد', '2021-01-25', parent_ids[0], False),  # طفل ثاني لنفس الوالد
        ('سارة علي', '2020-07-30', parent_ids[1], False),   # طفل ثاني لنفس الوالد
        ('حسام خالد', '2021-09-12', parent_ids[2], False),  # طفل ثالث منتظر الموافقة
    ]
    
    child_ids = []
    for name, birthdate, parent_id, is_approved in children_data:
        qr_code = generate_qr_code()
        cursor.execute('''
            INSERT INTO children (name, birthdate, parent_id, qr_code, is_approved)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, birthdate, parent_id, qr_code, is_approved))
        child_ids.append(cursor.lastrowid)
    
    # إنشاء سجلات حضور للأسبوع الماضي
    approved_children = child_ids[:5]  # الأطفال المقبولين فقط
    
    for day_offset in range(7):
        date = datetime.now() - timedelta(days=day_offset)
        
        for child_id in approved_children:
            # احتمالية حضور 85%
            if random.random() < 0.85:
                staff_id = random.choice(staff_ids)
                
                # تسجيل دخول
                check_in_time = date.replace(hour=random.randint(7, 9), minute=random.randint(0, 59))
                cursor.execute('''
                    INSERT INTO attendance (child_id, staff_id, status, timestamp, notes)
                    VALUES (?, ?, ?, ?, ?)
                ''', (child_id, staff_id, 'check_in', check_in_time, 'حضور عادي'))
                
                # تسجيل خروج (احتمالية 90%)
                if random.random() < 0.9:
                    check_out_time = date.replace(hour=random.randint(14, 16), minute=random.randint(0, 59))
                    cursor.execute('''
                        INSERT INTO attendance (child_id, staff_id, status, timestamp, notes)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (child_id, staff_id, 'check_out', check_out_time, 'انصراف عادي'))
    
    # إنشاء تحديثات يومية
    activity_types = [
        ('أكل', '🍽️'),
        ('نوم', '😴'),
        ('لعب', '🎮'),
        ('تعلم', '📚'),
        ('رياضة', '⚽'),
        ('فن', '🎨'),
        ('موسيقى', '🎵'),
        ('طبي', '🏥')
    ]
    
    sample_notes = [
        'تناول وجبة الإفطار بشهية جيدة',
        'نام لمدة ساعتين بهدوء',
        'لعب مع الأطفال الآخرين بمرح',
        'تعلم الحروف الجديدة بحماس',
        'مارس الرياضة في الحديقة',
        'رسم لوحة جميلة بالألوان',
        'غنى أغنية جديدة مع المجموعة',
        'فحص طبي روتيني - كل شيء طبيعي',
        'شارك في النشاط الجماعي',
        'أظهر تحسناً في المهارات الحركية',
    ]
    
    for day_offset in range(5):  # آخر 5 أيام
        date = datetime.now() - timedelta(days=day_offset)
        
        for child_id in approved_children:
            # إنشاء 2-4 تحديثات لكل طفل يومياً
            num_updates = random.randint(2, 4)
            
            for _ in range(num_updates):
                activity_type, icon = random.choice(activity_types)
                note = random.choice(sample_notes)
                staff_id = random.choice(staff_ids)
                
                update_time = date.replace(
                    hour=random.randint(8, 15),
                    minute=random.randint(0, 59)
                )
                
                cursor.execute('''
                    INSERT INTO daily_updates (child_id, staff_id, activity_type, note, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (child_id, staff_id, activity_type, note, update_time))
    
    conn.commit()
    conn.close()
    
    print("✅ تم إنشاء البيانات التجريبية بنجاح!")
    print("\n📊 البيانات المُنشأة:")
    print("- 1 مدير")
    print("- 3 موظفين")
    print("- 5 أولياء أمور")
    print("- 8 أطفال (5 مقبولين، 3 في الانتظار)")
    print("- سجلات حضور لآخر 7 أيام")
    print("- تحديثات يومية لآخر 5 أيام")
    
    print("\n🔐 بيانات تسجيل الدخول:")
    print("المدير: admin@brightkids.com / admin123")
    print("الموظف: fatima@brightkids.com / staff123")
    print("ولي الأمر: mohammed.parent@gmail.com / parent123")

if __name__ == '__main__':
    create_test_data()

