import requests
import json

BASE_URL = "https://j6h5i7cpv6ny.manus.space/api"

def create_user(endpoint, user_data):
    url = f"{BASE_URL}/{endpoint}"
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, headers=headers, json=user_data)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating user: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response content: {e.response.text}")
        return None

# بيانات الموظف الجديد
new_staff_data = {
    "name": "موظف جديد",
    "email": "new.staff@brightkids.com",
    "phone": "0551234567",
    "password": "newstaff123"
}

# بيانات ولي الأمر الجديد
new_parent_data = {
    "name": "ولي أمر جديد",
    "email": "new.parent@gmail.com",
    "phone": "0557654321",
    "password": "newparent123"
}

print("إنشاء موظف جديد...")
staff_response = create_user("auth/register/staff", new_staff_data)
if staff_response:
    print("✅ تم إنشاء الموظف الجديد بنجاح:")
    print(json.dumps(staff_response, indent=2, ensure_ascii=False))
    print(f'البريد الإلكتروني: {new_staff_data["email"]}')
    print(f'كلمة المرور: {new_staff_data["password"]}')
else:
    print("❌ فشل إنشاء الموظف الجديد.")

print("\nإنشاء ولي أمر جديد...")
parent_response = create_user("auth/register/parent", new_parent_data)
if parent_response:
    print("✅ تم إنشاء ولي الأمر الجديد بنجاح:")
    print(json.dumps(parent_response, indent=2, ensure_ascii=False))
    print(f'البريد الإلكتروني: {new_parent_data["email"]}')
    print(f'كلمة المرور: {new_parent_data["password"]}')
else:
    print("❌ فشل إنشاء ولي الأمر الجديد.")


