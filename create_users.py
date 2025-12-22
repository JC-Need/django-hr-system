import os
import django

# 1. ตั้งค่าระบบ
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mycompany.settings')
django.setup()

from django.contrib.auth.models import User
from employees.models import Employee

print("🚀 กำลังสร้างบัญชีผู้ใช้และจับคู่พนักงาน...")

employees = Employee.objects.all()

for emp in employees:
    # ข้ามคนที่จับคู่ไปแล้ว
    if emp.user:
        print(f"🔹 {emp.name} มีคู่แล้ว ({emp.user.username}) - ข้าม")
        continue

    # สร้าง Username จากรหัสพนักงาน (ตัดขีดออก ให้พิมพ์ง่ายๆ)
    # เช่น CEO-001 -> ceo001, STF-001 -> stf001
    if emp.emp_id:
        username = emp.emp_id.replace("-", "").lower()
    else:
        username = f"user{emp.id}"

    # ตรวจสอบว่ามี User นี้หรือยัง?
    user, created = User.objects.get_or_create(username=username)
    
    if created:
        # ถ้าเพิ่งสร้างใหม่ ให้ตั้งรหัสผ่านเป็น '1234'
        user.set_password('1234')
        user.save()
        status = "สร้างใหม่"
    else:
        status = "ใช้ของเดิม"

    # จับคู่! 💍
    emp.user = user
    emp.save()
    
    print(f"✅ {emp.name} : จับคู่กับ User '{username}' ({status})")

print("\n🎉 เรียบร้อย! พนักงานทุกคนล็อกอินได้แล้ว (รหัสผ่าน 1234)")