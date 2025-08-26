from flask import Blueprint, request, jsonify
from datetime import datetime
import uuid
import os
from werkzeug.utils import secure_filename

registration_bp = Blueprint('registration', __name__)

# مجلد لحفظ الملفات المرفوعة
UPLOAD_FOLDER = 'uploads/registrations'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_folder():
    """التأكد من وجود مجلد الرفع"""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

@registration_bp.route('/api/registration/submit', methods=['POST'])
def submit_registration():
    """استقبال طلب تسجيل طفل جديد"""
    try:
        ensure_upload_folder()
        
        # إنشاء رقم تسجيل فريد
        registration_number = f"BK-{str(uuid.uuid4())[:6].upper()}"
        
        # استخراج البيانات من النموذج
        data = {}
        
        # بيانات الطفل
        data['child_name'] = request.form.get('childName', '')
        data['birth_date'] = request.form.get('birthDate', '')
        data['age'] = request.form.get('age', '')
        data['gender'] = request.form.get('gender', '')
        data['nationality'] = request.form.get('nationality', '')
        data['birth_place'] = request.form.get('birthPlace', '')
        
        # بيانات ولي الأمر
        data['parent_name'] = request.form.get('parentName', '')
        data['relationship'] = request.form.get('relationship', '')
        data['phone_number'] = request.form.get('phoneNumber', '')
        data['emergency_phone'] = request.form.get('emergencyPhone', '')
        data['email'] = request.form.get('email', '')
        data['address'] = request.form.get('address', '')
        
        # معالجة الملفات المرفوعة
        uploaded_files = []
        for file_key in request.files:
            file = request.files[file_key]
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # إضافة timestamp لتجنب تضارب الأسماء
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{registration_number}_{timestamp}_{filename}"
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                uploaded_files.append({
                    'original_name': file.filename,
                    'saved_name': filename,
                    'file_path': file_path,
                    'file_type': file_key
                })
        
        # إنشاء سجل التسجيل
        registration_record = {
            'registration_number': registration_number,
            'submission_date': datetime.now().isoformat(),
            'status': 'pending_review',  # قيد المراجعة
            'child_data': {
                'name': data['child_name'],
                'birth_date': data['birth_date'],
                'age': data['age'],
                'gender': data['gender'],
                'nationality': data['nationality'],
                'birth_place': data['birth_place']
            },
            'parent_data': {
                'name': data['parent_name'],
                'relationship': data['relationship'],
                'phone': data['phone_number'],
                'emergency_phone': data['emergency_phone'],
                'email': data['email'],
                'address': data['address']
            },
            'uploaded_files': uploaded_files,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # حفظ السجل في ملف JSON مؤقت (يمكن استبداله بقاعدة بيانات لاحقاً)
        import json
        registrations_file = 'data/registrations.json'
        
        # التأكد من وجود مجلد البيانات
        if not os.path.exists('data'):
            os.makedirs('data')
        
        # قراءة السجلات الموجودة أو إنشاء قائمة جديدة
        registrations = []
        if os.path.exists(registrations_file):
            try:
                with open(registrations_file, 'r', encoding='utf-8') as f:
                    registrations = json.load(f)
            except:
                registrations = []
        
        # إضافة السجل الجديد
        registrations.append(registration_record)
        
        # حفظ السجلات المحدثة
        with open(registrations_file, 'w', encoding='utf-8') as f:
            json.dump(registrations, f, ensure_ascii=False, indent=2)
        
        # إرسال استجابة النجاح
        return jsonify({
            'success': True,
            'message': 'تم إرسال طلب التسجيل بنجاح',
            'registration_number': registration_number,
            'status': 'pending_review',
            'submission_date': registration_record['submission_date'],
            'ticket_data': {
                'registration_number': registration_number,
                'child_name': data['child_name'],
                'parent_name': data['parent_name'],
                'phone': data['phone_number'],
                'email': data['email'],
                'submission_date': datetime.now().strftime('%Y-%m-%d'),
                'status': 'قيد المراجعة',
                'nursery_info': {
                    'name': 'مركز Bright Kids للحضانة',
                    'license': 'YADC7069',
                    'address': 'حي قرطبة، 46429، ينبع',
                    'phone': '+966 53 750 6160'
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'حدث خطأ أثناء معالجة الطلب: {str(e)}'
        }), 500

@registration_bp.route('/api/registration/list', methods=['GET'])
def list_registrations():
    """عرض قائمة طلبات التسجيل"""
    try:
        import json
        registrations_file = 'data/registrations.json'
        
        if not os.path.exists(registrations_file):
            return jsonify({
                'success': True,
                'registrations': [],
                'total': 0
            })
        
        with open(registrations_file, 'r', encoding='utf-8') as f:
            registrations = json.load(f)
        
        # ترتيب حسب تاريخ التقديم (الأحدث أولاً)
        registrations.sort(key=lambda x: x['submission_date'], reverse=True)
        
        return jsonify({
            'success': True,
            'registrations': registrations,
            'total': len(registrations)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'حدث خطأ أثناء جلب البيانات: {str(e)}'
        }), 500

@registration_bp.route('/api/registration/<registration_number>', methods=['GET'])
def get_registration(registration_number):
    """عرض تفاصيل طلب تسجيل محدد"""
    try:
        import json
        registrations_file = 'data/registrations.json'
        
        if not os.path.exists(registrations_file):
            return jsonify({
                'success': False,
                'message': 'لم يتم العثور على الطلب'
            }), 404
        
        with open(registrations_file, 'r', encoding='utf-8') as f:
            registrations = json.load(f)
        
        # البحث عن الطلب
        registration = None
        for reg in registrations:
            if reg['registration_number'] == registration_number:
                registration = reg
                break
        
        if not registration:
            return jsonify({
                'success': False,
                'message': 'لم يتم العثور على الطلب'
            }), 404
        
        return jsonify({
            'success': True,
            'registration': registration
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'حدث خطأ أثناء جلب البيانات: {str(e)}'
        }), 500

@registration_bp.route('/api/registration/<registration_number>/status', methods=['PUT'])
def update_registration_status(registration_number):
    """تحديث حالة طلب التسجيل"""
    try:
        import json
        registrations_file = 'data/registrations.json'
        
        if not os.path.exists(registrations_file):
            return jsonify({
                'success': False,
                'message': 'لم يتم العثور على الطلب'
            }), 404
        
        data = request.get_json()
        new_status = data.get('status')
        notes = data.get('notes', '')
        
        # قراءة السجلات
        with open(registrations_file, 'r', encoding='utf-8') as f:
            registrations = json.load(f)
        
        # البحث عن الطلب وتحديثه
        updated = False
        for reg in registrations:
            if reg['registration_number'] == registration_number:
                reg['status'] = new_status
                reg['updated_at'] = datetime.now().isoformat()
                if notes:
                    if 'notes' not in reg:
                        reg['notes'] = []
                    reg['notes'].append({
                        'note': notes,
                        'timestamp': datetime.now().isoformat()
                    })
                updated = True
                break
        
        if not updated:
            return jsonify({
                'success': False,
                'message': 'لم يتم العثور على الطلب'
            }), 404
        
        # حفظ التحديثات
        with open(registrations_file, 'w', encoding='utf-8') as f:
            json.dump(registrations, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'success': True,
            'message': 'تم تحديث حالة الطلب بنجاح'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'حدث خطأ أثناء التحديث: {str(e)}'
        }), 500

@registration_bp.route('/api/registration/stats', methods=['GET'])
def get_registration_stats():
    """إحصائيات طلبات التسجيل"""
    try:
        import json
        registrations_file = 'data/registrations.json'
        
        if not os.path.exists(registrations_file):
            return jsonify({
                'success': True,
                'stats': {
                    'total': 0,
                    'pending': 0,
                    'approved': 0,
                    'rejected': 0,
                    'today': 0,
                    'this_week': 0,
                    'this_month': 0
                }
            })
        
        with open(registrations_file, 'r', encoding='utf-8') as f:
            registrations = json.load(f)
        
        from datetime import datetime, timedelta
        
        now = datetime.now()
        today = now.date()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        stats = {
            'total': len(registrations),
            'pending': 0,
            'approved': 0,
            'rejected': 0,
            'today': 0,
            'this_week': 0,
            'this_month': 0
        }
        
        for reg in registrations:
            # إحصائيات الحالة
            status = reg.get('status', 'pending_review')
            if status == 'pending_review':
                stats['pending'] += 1
            elif status == 'approved':
                stats['approved'] += 1
            elif status == 'rejected':
                stats['rejected'] += 1
            
            # إحصائيات التاريخ
            submission_date = datetime.fromisoformat(reg['submission_date']).date()
            if submission_date == today:
                stats['today'] += 1
            if datetime.fromisoformat(reg['submission_date']) >= week_ago:
                stats['this_week'] += 1
            if datetime.fromisoformat(reg['submission_date']) >= month_ago:
                stats['this_month'] += 1
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'حدث خطأ أثناء جلب الإحصائيات: {str(e)}'
        }), 500

