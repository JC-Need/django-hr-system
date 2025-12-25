from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from .models import Employee, Attendance, LeaveRequest
from .forms import LeaveRequestForm
import datetime

# --- ฟังก์ชันช่วย: ดึงข้อมูลพนักงานจาก User ---
def get_employee_from_user(user):
    if hasattr(user, 'employee'):
        return user.employee
    elif hasattr(user, 'employee_profile'):
        return user.employee_profile
    return None

# --- ฟังก์ชันเช็คว่าเป็น Admin ---
def is_admin(user):
    return user.is_superuser

# ==========================================
# 1. หน้า Dashboard
# ==========================================
@login_required
def dashboard(request):
    if not request.user.is_superuser:
        emp = get_employee_from_user(request.user)
        if emp:
            return redirect('employee_detail', emp_id=emp.id)
        else:
            return render(request, 'employees/login.html', {
                'form': None, 
                'error': 'บัญชีนี้ไม่มีข้อมูลพนักงานในระบบ (กรุณาติดต่อ HR)'
            })

    employees = Employee.objects.all()
    # คำนวณเงินเดือนรวม
    total_salary = sum(emp.base_allowance for emp in employees if emp.base_allowance)
    pending_leaves = LeaveRequest.objects.filter(status='PENDING').order_by('-start_date')

    context = {
        'total_employees': employees.count(),
        'total_salary': "{:,.2f}".format(total_salary),
        'employees': employees,
        'pending_leaves': pending_leaves,
    }
    return render(request, 'employees/dashboard.html', context)

# ==========================================
# 2. หน้าประวัติพนักงาน (แก้ไขจุด Error แล้ว!)
# ==========================================
@login_required
def employee_detail(request, emp_id):
    employee = get_object_or_404(Employee, pk=emp_id)
    
    # ✅ ลบโค้ดบรรทัดที่ error ทิ้งแล้ว (เพราะ Models จัดการให้อัตโนมัติ)
    
    # 1. ประวัติเข้างาน & สถานะ
    attendance_list = Attendance.objects.filter(employee=employee).order_by('-date')
    start_work_time = datetime.time(9, 0, 0) 

    for att in attendance_list:
        if att.time_in:
            check_time = att.time_in
            if isinstance(check_time, datetime.datetime): check_time = check_time.time()
                
            if check_time > start_work_time:
                att.status_label = "มาสาย ⚠️"
                att.status_color = "warning"
            else:
                att.status_label = "ปกติ ✅"
                att.status_color = "success"
        else:
            att.status_label = "ขาดงาน ❌"
            att.status_color = "danger"

    # 2. ประวัติการลา
    leave_list = LeaveRequest.objects.filter(employee=employee).order_by('-start_date')
    
    # 3. คำนวณโบนัส
    base_bonus = 10000 
    sick_count = LeaveRequest.objects.filter(employee=employee, leave_type='SICK', status='APPROVED').count()
    business_count = LeaveRequest.objects.filter(employee=employee, leave_type='BUSINESS', status='APPROVED').count()
    
    sick_deduct = sick_count * 500
    business_deduct = business_count * 1000
    total_deduct = sick_deduct + business_deduct
    
    final_bonus_val = max(0, base_bonus - total_deduct)
    formatted_bonus = "{:,.2f}".format(final_bonus_val)
    
    # ส่งข้อมูลไปหน้าเว็บ
    return render(request, 'employees/employee_detail.html', {
        'employee': employee,
        'attendance_list': attendance_list,
        'leave_list': leave_list,
        'formatted_bonus': formatted_bonus,
        'total_deduct': "{:,.0f}".format(total_deduct),
        
        # ข้อมูลสำหรับ Popup รายละเอียดโบนัส
        'base_bonus': "{:,.0f}".format(base_bonus),
        'sick_count': sick_count,
        'sick_deduct': "{:,.0f}".format(sick_deduct),
        'business_count': business_count,
        'business_deduct': "{:,.0f}".format(business_deduct),
    })

# ==========================================
# 3. ระบบลางาน
# ==========================================
@login_required
def leave_create(request):
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            emp = get_employee_from_user(request.user)
            if emp:
                leave.employee = emp
                leave.save()
                messages.success(request, 'ส่งใบลาเรียบร้อยแล้ว')
                return redirect('employee_detail', emp_id=emp.id)
            else:
                messages.error(request, 'ไม่พบข้อมูลพนักงาน')
    else:
        form = LeaveRequestForm()
    
    return render(request, 'employees/leave_form.html', {'form': form})

# ==========================================
# 4. ฟังก์ชันอื่นๆ (แก้สลิปเงินเดือนให้ด้วย)
# ==========================================
@login_required
def employee_payslip(request, emp_id):
    employee = get_object_or_404(Employee, pk=emp_id)
    
    # คำนวณเป็นตัวเลขก่อน (แปลง Decimal เป็น float เพื่อคำนวณ)
    salary = float(employee.base_allowance)
    
    # ประกันสังคม 5% (สูงสุด 750)
    sso_val = min(salary * 0.05, 750.0)
    
    total_income = salary
    net_salary = total_income - sso_val
    
    # ส่งค่าแบบจัดรูปแบบ (มีลูกน้ำ) ไปที่หน้าเว็บ
    return render(request, 'employees/payslip.html', {
        'employee': employee,
        'salary': "{:,.2f}".format(salary),
        'total_income': "{:,.2f}".format(total_income),
        'sso': "{:,.2f}".format(sso_val),
        'net_salary': "{:,.2f}".format(net_salary),
        'today': timezone.now(),
    })

@login_required
@user_passes_test(is_admin)
def leave_approval(request):
    leaves = LeaveRequest.objects.filter(status='PENDING').order_by('-created_at')
    return render(request, 'employees/leave_approval.html', {'leaves': leaves})

@login_required
@user_passes_test(is_admin)
def approve_leave(request, leave_id):
    leave = get_object_or_404(LeaveRequest, pk=leave_id)
    leave.status = 'APPROVED'
    leave.save()
    return redirect('dashboard')

@login_required
@user_passes_test(is_admin)
def reject_leave(request, leave_id):
    leave = get_object_or_404(LeaveRequest, pk=leave_id)
    leave.status = 'REJECTED'
    leave.save()
    return redirect('dashboard')

@login_required
@user_passes_test(is_admin)
def calculate_bonus(request):
    return redirect('dashboard')

@login_required
@user_passes_test(is_admin)
def delete_employee(request, emp_id):
    emp = get_object_or_404(Employee, pk=emp_id)
    emp.delete()
    return redirect('dashboard')

@login_required
def attendance_action(request, emp_id):
    employee = get_object_or_404(Employee, pk=emp_id)
    today = timezone.now().date()
    now_time = timezone.now().time()
    attendance, created = Attendance.objects.get_or_create(employee=employee, date=today)
    
    if not attendance.time_in:
        attendance.time_in = now_time
    elif not attendance.time_out:
        attendance.time_out = now_time
        
    attendance.save()
    return redirect('employee_detail', emp_id=emp_id)