from django.shortcuts import render, redirect, get_object_or_404
from .models import Employee
from .forms import EmployeeForm  # <--- 1. อย่าลืมบรรทัดนี้! เรียกใช้ฟอร์มที่เพิ่งสร้าง

def dashboard(request):
    # --- ส่วนที่ 1: จัดการการเพิ่มพนักงาน (POST Request) ---
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()  # บันทึกลง Database ทันที
            return redirect('/')  # รีเฟรชหน้าจอใหม่
    else:
        form = EmployeeForm() # ถ้าเพิ่งเข้ามา ให้สร้างฟอร์มเปล่าๆ เตรียมไว้

    # --- ส่วนที่ 2: คำนวณเงินโบนัส (เหมือนเดิม) ---
    raw_profit = request.GET.get('profit', '0')
    clean_profit = raw_profit.replace(',', '')
    try:
        total_bonus_pool = float(clean_profit)
    except ValueError:
        total_bonus_pool = 0.0

    all_employees = Employee.objects.all()
    total_weight = sum(float(emp.level_weight) for emp in all_employees)

    for emp in all_employees:
        if total_weight > 0:
            ratio = float(emp.level_weight) / total_weight
            bonus = ratio * total_bonus_pool
            emp.bonus_amount = f"{bonus:,.2f}"
        else:
            emp.bonus_amount = "0.00"

    # --- ส่วนที่ 3: ส่งของไปหน้าเว็บ ---
    context = {
        'form': form,  # ส่งฟอร์มไปให้หน้าเว็บวาด
        'profit_input': f"{total_bonus_pool:,.2f}",
        'profit': total_bonus_pool,
        'total_weight': total_weight,
        'employees': all_employees,
    }

    return render(request, 'employees/dashboard.html', context)

# (ฟังก์ชัน delete_employee ปล่อยไว้เหมือนเดิมครับ)
def delete_employee(request, emp_id):
    emp = get_object_or_404(Employee, id=emp_id)
    emp.delete()
    return redirect('/')