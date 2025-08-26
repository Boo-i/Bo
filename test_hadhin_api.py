import requests
import json

BASE_URL = "https://j6h5i7cpv6ny.manus.space/api"

def register_parent(name, email, phone, password):
    print(f"\n--- تسجيل ولي أمر جديد: {email} ---")
    url = f"{BASE_URL}/auth/register/parent"
    payload = {
        "name": name,
        "email": email,
        "phone": phone,
        "password": password
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print("✅ تم التسجيل بنجاح:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ فشل التسجيل: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"الاستجابة: {e.response.text}")
        return None

def login_user(email, password):
    print(f"\n--- تسجيل الدخول للمستخدم: {email} ---")
    url = f"{BASE_URL}/auth/login"
    payload = {
        "email": email,
        "password": password
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print("✅ تم تسجيل الدخول بنجاح:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        return response.json().get("token")
    except requests.exceptions.RequestException as e:
        print(f"❌ فشل تسجيل الدخول: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"الاستجابة: {e.response.text}")
        return None

def add_child(token, name, birthdate):
    print(f"\n--- إضافة طفل جديد: {name} ---")
    url = f"{BASE_URL}/children/add"
    payload = {
        "name": name,
        "birthdate": birthdate
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print("✅ تم إضافة الطفل بنجاح:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ فشل إضافة الطفل: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"الاستجابة: {e.response.text}")
        return None

# بيانات ولي الأمر الجديد للاختبار
new_parent_name = "أحمد علي"
new_parent_email = "ahmed.ali.new@example.com"
new_parent_phone = "0501234567"
new_parent_password = "password123"

# 1. تسجيل ولي أمر جديد
registration_result = register_parent(new_parent_name, new_parent_email, new_parent_phone, new_parent_password)

if registration_result:
    # 2. تسجيل الدخول بولي الأمر الجديد للحصول على التوكن
    access_token = login_user(new_parent_email, new_parent_password)

    if access_token:
        # 3. إضافة طفل جديد باستخدام التوكن
        add_child(access_token, "ليلى أحمد", "2022-03-10")
    else:
        print("لا يمكن إضافة طفل بدون توكن الوصول.")
else:
    print("لا يمكن تسجيل الدخول أو إضافة طفل بدون تسجيل ولي الأمر.")


