from django.db.models import Sum, Count
import json
from datetime import timedelta  # เพิ่มตัวนี้เข้ามาด้วยนะครับ
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
# 1. หน้า Dashboard (แก้ไขใหม่: เตรียมทำกราฟสวยๆ)
# ==========================================
@login_required
def dashboard(request):
    # 1. ป้องกันพนักงานทั่วไป (เหมือนเดิม)
    if not request.user.is_superuser:
        emp = get_employee_from_user(request.user)
        if emp:
            return redirect('employee_detail', emp_id=emp.id)
        else:
            return render(request, 'employees/login.html', {'form': None, 'error': 'Access Denied'})

    # 2. เตรียมข้อมูลจริง (Calculations)
    today = timezone.now().date()

    # --- ข้อมูลการ์ด 4 ใบ ---
    total_employees = Employee.objects.count()

    # รวมเงินเดือน (ถ้าไม่มีข้อมูลให้เป็น 0)
    total_salary = Employee.objects.aggregate(Sum('base_allowance'))['base_allowance__sum'] or 0

    pending_leaves = LeaveRequest.objects.filter(status='PENDING').count()

    # ขาดงานวันนี้ (จำนวนพนักงานทั้งหมด - จำนวนคนที่เช็คชื่อวันนี้)
    present_count = Attendance.objects.filter(date=today).count()
    absent_today = total_employees - present_count
    # [ใหม่ 2] --- เจาะลึกคนขาด/คนลา (Absence Insight) ---
    # 1. ดึงรายชื่อคนที่ "ลาวันนี้" (สถานะ APPROVED)
    on_leave_list = LeaveRequest.objects.filter(
        start_date__lte=today,
        end_date__gte=today,
        status='APPROVED'
    )
    # 2. ดึงรายชื่อคนที่ "ขาดงาน" (ไม่ได้มาทำงาน และ ไม่ได้ลา)
    # 2.1 หา ID คนที่มาทำงานแล้ว
    present_ids = Attendance.objects.filter(date=today).values_list('employee_id', flat=True)
    # 2.2 หา ID คนที่ลาวันนี้
    leave_ids = on_leave_list.values_list('employee_id', flat=True)

    # 2.3 คัดกรอง: เอาพนักงานทั้งหมด "ลบ" คนมา "ลบ" คนลา = คนขาดงานจริงๆ
    absent_list = Employee.objects.exclude(id__in=present_ids).exclude(id__in=leave_ids)
    # [ใหม่] --- ข้อมูลแยกตามแผนก (Department Analysis) ---
    # คำสั่งนี้จะจัดกลุ่มตาม 'department' แล้วนับจำนวนคน (count) และรวมเงินเดือน (sum)
    dept_summary = Employee.objects.values('department').annotate(
        count=Count('id'),
        total_salary=Sum('base_allowance')
    ).order_by('-total_salary') # เรียงตามเงินเดือนมากไปน้อย

    # --- ข้อมูลกราฟแท่ง (Bar Chart): สถิติคนมาทำงาน 7 วันย้อนหลัง ---
    bar_labels = [] # วันที่
    bar_data = []   # จำนวนคน
    for i in range(6, -1, -1): # วนลูปย้อนหลัง 6 วัน ถึงวันนี้
        check_date = today - timedelta(days=i)
        count = Attendance.objects.filter(date=check_date).count()
        # แปลงวันที่เป็น text สั้นๆ เช่น "26/12"
        bar_labels.append(check_date.strftime('%d/%m'))
        bar_data.append(count)

    # --- ข้อมูลกราฟวงกลม (Pie Chart): สรุปสถานะวันนี้ (มาปกติ / สาย / ขาด) ---
    # สมมติเวลาเข้างาน 09:00
    start_work_time = datetime.time(9, 0, 0)
    late_count = Attendance.objects.filter(date=today, time_in__gt=start_work_time).count()
    on_time_count = present_count - late_count

    # ส่งข้อมูลเข้ากล่อง Context
    # [ใหม่ 3] --- Activity Feed (ความเคลื่อนไหวล่าสุดวันนี้) ---
    activities = []

    # 1. ดึงคน "เข้างาน" วันนี้
    recent_atts = Attendance.objects.filter(date=today, time_in__isnull=False)
    for att in recent_atts:
        activities.append({
            'time': att.time_in, # เวลาเข้า
            'text': f"{att.employee.first_name} ลงเวลาเข้างาน",
            'icon': 'fa-fingerprint', # ไอคอนนิ้วมือ
            'color': 'text-success',  # สีเขียว
            'bg': 'bg-success-subtle' # พื้นหลังจางๆ
        })

    # 2. ดึงคน "ยื่นใบลา" วันนี้
    # (ใช้ created_at__date=today เพื่อดูเฉพาะที่ยื่นวันนี้)
    recent_leaves = LeaveRequest.objects.filter(created_at__date=today)
    for leave in recent_leaves:
        # แปลงเวลาให้เป็น Local Time เพื่อแสดงผล
        local_time = timezone.localtime(leave.created_at).time()
        activities.append({
            'time': local_time,
            'text': f"{leave.employee.first_name} ยื่นใบลา ({leave.leave_type})",
            'icon': 'fa-paper-plane', # ไอคอนจรวดกระดาษ
            'color': 'text-warning',  # สีส้ม
            'bg': 'bg-warning-subtle'
        })

    # 3. เรียงลำดับตามเวลา (ล่าสุดขึ้นก่อน)
    activities.sort(key=lambda x: x['time'], reverse=True)
    context = {
        # การ์ด
        'total_employees': total_employees,
        'total_salary': "{:,.2f}".format(total_salary),
        'pending_leaves': pending_leaves,
        'absent_today': absent_today,

        # กราฟ (ต้องแปลงเป็น JSON เพื่อส่งให้ JavaScript อ่าน)
        'bar_labels': json.dumps(bar_labels),
        'bar_data': json.dumps(bar_data),
        'pie_data': json.dumps([on_time_count, late_count, absent_today]),
        'dept_summary': dept_summary,
        # [ใหม่] ส่งรายชื่อไปหน้าเว็บ
        'on_leave_list': on_leave_list,
        'absent_list': absent_list,
	# [ใหม่] ส่ง Activity Feed ไปหน้าเว็บ
        'activities': activities[:6], # ส่งไปแค่ 6 รายการล่าสุดพอ (กันรก)
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

# ==========================================
# 5. หน้ารายละเอียดแผนก (Department Detail)
# ==========================================
@login_required
def department_detail(request, dept_name):
    # ดึงรายชื่อพนักงาน โดยกรองเฉพาะแผนกที่ส่งมา (dept_name)
    employees = Employee.objects.filter(department=dept_name)

    context = {
        'dept_name': dept_name,
        'employees': employees,
    }
    return render(request, 'employees/department_detail.html', context)