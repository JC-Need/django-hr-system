import os
import django

# 1. ตั้งค่า Environment ให้รู้จัก Django
# (ถ้าโปรเจกต์คุณชื่ออื่นที่ไม่ใช่ mycompany ให้แก้ตรงนี้)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mycompany.settings')
django.setup()

from django.contrib.auth.models import User
from employees.models import Employee
from datetime import date

# 2. ข้อมูลพนักงาน 20 คน
employees_data = [
    # --- HR ---
    {"u": "hr_suda", "f": "สุดา", "l": "ใจดี", "pos": "HR Manager", "dept": "Human Resources"},
    {"u": "hr_wipa", "f": "วิภา", "l": "รักงาน", "pos": "Recruiter", "dept": "Human Resources"},
    {"u": "hr_karn", "f": "กานต์", "l": "ธุรการ", "pos": "Admin Staff", "dept": "Human Resources"},
    
    # --- IT ---
    {"u": "it_somchai", "f": "สมชาย", "l": "เก่งมาก", "pos": "IT Manager", "dept": "IT Support"},
    {"u": "it_ek", "f": "เอก", "l": "โปรแกรม", "pos": "Senior Developer", "dept": "IT Support"},
    {"u": "it_to", "f": "โท", "l": "ระบบ", "pos": "System Admin", "dept": "IT Support"},
    {"u": "it_tree", "f": "ตรี", "l": "ซ่อมไว", "pos": "IT Support", "dept": "IT Support"},
    {"u": "it_jattawa", "f": "จัตวา", "l": "ดีไซน์", "pos": "UX/UI Designer", "dept": "IT Support"},

    # --- Sales ---
    {"u": "sale_mana", "f": "มานะ", "l": "ขายเก่ง", "pos": "Sales Manager", "dept": "Sales"},
    {"u": "sale_manee", "f": "มานี", "l": "มีเงิน", "pos": "Sales Executive", "dept": "Sales"},
    {"u": "sale_piti", "f": "ปิติ", "l": "ยอดนักขาย", "pos": "Sales Executive", "dept": "Sales"},
    {"u": "sale_chujai", "f": "ชูใจ", "l": "ขายดี", "pos": "Sales Admin", "dept": "Sales"},
    {"u": "sale_weera", "f": "วีระ", "l": "ลูกค้าเยอะ", "pos": "Account Executive", "dept": "Sales"},

    # --- Finance ---
    {"u": "fin_malee", "f": "มาลี", "l": "มีทอง", "pos": "Finance Manager", "dept": "Finance"},
    {"u": "fin_somsri", "f": "สมศรี", "l": "ขยันเก็บ", "pos": "Accountant", "dept": "Finance"},
    {"u": "fin_somsak", "f": "สมศักดิ์", "l": "จ่ายไว", "pos": "Payroll Officer", "dept": "Finance"},

    # --- Marketing ---
    {"u": "mkt_fah", "f": "ฟ้าใส", "l": "ไอเดีย", "pos": "Marketing Manager", "dept": "Marketing"},
    {"u": "mkt_tawan", "f": "ตะวัน", "l": "คอนเทนต์", "pos": "Content Creator", "dept": "Marketing"},

    # --- Operations ---
    {"u": "op_kla", "f": "กล้า", "l": "ลุยงาน", "pos": "Operations Manager", "dept": "Operations"},
    {"u": "op_kaew", "f": "แก้ว", "l": "จัดการ", "pos": "Operations Staff", "dept": "Operations"},
]

print("🚀 กำลังเริ่มสร้างพนักงานจำลอง...")

# 3. ลูปสร้างข้อมูล
for data in employees_data:
    username = data["u"]
    password = "1234"
    
    # ตรวจสอบว่ามี User นี้หรือยัง
    if User.objects.filter(username=username).exists():
        print(f"⚠️  ข้าม: {username} มีอยู่ในระบบแล้ว")
        user = User.objects.get(username=username)
    else:
        # สร้าง User ใหม่
        user = User.objects.create_user(username=username, password=password)
        print(f"✅ สร้าง User: {username}")

    # ตรวจสอบว่าผูกกับ Employee หรือยัง
    if not hasattr(user, 'employee'):
        Employee.objects.create(
            user=user,
            employee_id=f"EMP_{username.upper()}", # สร้างรหัสพนักงานให้อัตโนมัติ
            first_name=data["f"],
            last_name=data["l"],
            position=data["pos"],
            department=data["dept"],
            base_allowance=15000 + (len(data["u"]) * 1000), # สุ่มเงินเดือนเล่นๆ ตามความยาวชื่อ
            joined_date=date.today()
        )
        print(f"   └── ผูกประวัติพนักงาน: {data['f']} {data['l']} สำเร็จ!")
    else:
        print(f"   └── {data['f']} มีประวัติอยู่แล้ว")

print("\n🎉 เสร็จสมบูรณ์! สร้างพนักงานครบแล้วครับ JC")