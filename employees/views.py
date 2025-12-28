from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.contrib.auth import login, logout
from django.db.models import Sum, Count
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Employee, Attendance, LeaveRequest
from .forms import LeaveRequestForm
from django.contrib.auth.models import User

import datetime
from datetime import timedelta
import json
import requests

# --- ฟังก์ชันช่วย ---
def get_employee_from_user(user):
    if hasattr(user, 'employee'):
        return user.employee
    elif hasattr(user, 'employee_profile'):
        return user.employee_profile
    return None

def is_admin(user):
    return user.is_superuser

# ==========================================
# 🤖 ฟังก์ชันส่ง LINE
# ==========================================
def send_line_alert(message, target_id=None):
    # 👇 Token ของคุณ
    LINE_TOKEN = 'R8cR4RQiDZA9sRljWNa8f6TaspfFYUxBoGaLNUAIBfaxD5iiN0jWiI2e34NAkXP36GBtALNyEk7foed2g1bdkArDqhA9NbhPeVqYqGdElngJt7+YHjdsiNv81geRXVfrKqD4UQABNNemXFfFwCW1uAdB04t89/1O/w1cDnyilFU='
    BOSS_ID = 'Ubb324ad1f45ef40d567ee70823007142'

    if target_id is None:
        target_id = BOSS_ID

    url = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_TOKEN}'
    }
    data = {
        'to': target_id,
        'messages': [{'type': 'text', 'text': message}]
    }

    try:
        requests.post(url, headers=headers, json=data)
        print(f"ส่ง LINE หา {target_id} สำเร็จ")
    except Exception as e:
        print(f"ส่ง LINE ผิดพลาด: {e}")

# ==========================================
# 0. หน้าแรก (Login)
# ==========================================
def home(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'employees/home.html', {'form': form})

# ==========================================
# 1. Dashboard
# ==========================================
@login_required
def dashboard(request):
    if not request.user.is_superuser:
        emp = get_employee_from_user(request.user)
        if emp:
            return redirect('employee_detail', emp_id=emp.id)
        else:
            return render(request, 'employees/login.html', {'form': None, 'error': 'Access Denied'})

    today = timezone.now().date()
    total_employees = Employee.objects.count()
    total_salary = Employee.objects.aggregate(Sum('base_allowance'))['base_allowance__sum'] or 0
    pending_leaves = LeaveRequest.objects.filter(status='PENDING').count()

    present_count = Attendance.objects.filter(date=today).count()
    absent_today = total_employees - present_count

    on_leave_list = LeaveRequest.objects.filter(start_date__lte=today, end_date__gte=today, status='APPROVED')
    present_ids = Attendance.objects.filter(date=today).values_list('employee_id', flat=True)
    leave_ids = on_leave_list.values_list('employee_id', flat=True)
    absent_list = Employee.objects.exclude(id__in=present_ids).exclude(id__in=leave_ids)

    dept_summary = Employee.objects.values('department').annotate(
        count=Count('id'), total_salary=Sum('base_allowance')
    ).order_by('-total_salary')

    bar_labels = []
    bar_data = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        bar_labels.append(d.strftime('%d/%m'))
        bar_data.append(Attendance.objects.filter(date=d).count())

    start_work_time = datetime.time(9, 0, 0)
    late_count = Attendance.objects.filter(date=today, time_in__gt=start_work_time).count()
    on_time_count = present_count - late_count

    activities = []
    recent_atts = Attendance.objects.filter(date=today, time_in__isnull=False)
    for att in recent_atts:
        activities.append({
            'time': att.time_in,
            'text': f"{att.employee.first_name} ลงเวลาเข้างาน",
            'icon': 'fa-fingerprint', 'color': 'text-success', 'bg': 'bg-success-subtle'
        })
    recent_leaves = LeaveRequest.objects.filter(created_at__date=today)
    for leave in recent_leaves:
        local_time = timezone.localtime(leave.created_at).time()
        activities.append({
            'time': local_time,
            'text': f"{leave.employee.first_name} ยื่นใบลา ({leave.leave_type})",
            'icon': 'fa-paper-plane', 'color': 'text-warning', 'bg': 'bg-warning-subtle'
        })
    activities.sort(key=lambda x: x['time'], reverse=True)

    context = {
        'total_employees': total_employees,
        'total_salary': "{:,.2f}".format(total_salary),
        'pending_leaves': pending_leaves,
        'absent_today': absent_today,
        'bar_labels': json.dumps(bar_labels),
        'bar_data': json.dumps(bar_data),
        'pie_data': json.dumps([on_time_count, late_count, absent_today]),
        'dept_summary': dept_summary,
        'on_leave_list': on_leave_list,
        'absent_list': absent_list,
        'activities': activities[:6],
    }
    return render(request, 'employees/dashboard.html', context)

# ==========================================
# 2. หน้าประวัติพนักงาน
# ==========================================
@login_required
def employee_detail(request, emp_id):
    employee = get_object_or_404(Employee, pk=emp_id)

    # 1. ดึงข้อมูลทั้งหมดมาก่อน (เรียงจากใหม่ไปเก่า)
    attendance_list = Attendance.objects.filter(employee=employee).order_by('-date')
    leave_list = LeaveRequest.objects.filter(employee=employee).order_by('-start_date')

    # 2. 👇👇 ส่วนกรองวันที่ (Search Logic) 👇👇
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        # กรองเวลาเข้า-ออก (ใช้ field 'date')
        attendance_list = attendance_list.filter(date__range=[start_date, end_date])
        # กรองประวัติการลา (เช็คว่าวันเริ่มลา อยู่ในช่วงที่เลือกไหม)
        leave_list = leave_list.filter(start_date__gte=start_date, start_date__lte=end_date)
    # 👆👆 -------------------------------- 👆👆

    # 3. คำนวณสถานะ มาสาย/ขาดงาน (Code เดิม)
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

    # 4. คำนวณโบนัส (Code เดิม)
    base_bonus = 10000
    sick_count = LeaveRequest.objects.filter(employee=employee, leave_type='SICK', status='APPROVED').count()
    business_count = LeaveRequest.objects.filter(employee=employee, leave_type='BUSINESS', status='APPROVED').count()
    total_deduct = (sick_count * 500) + (business_count * 1000)
    final_bonus_val = max(0, base_bonus - total_deduct)

    return render(request, 'employees/employee_detail.html', {
        'employee': employee,
        'attendance_list': attendance_list,
        'leave_list': leave_list,
        'formatted_bonus': "{:,.2f}".format(final_bonus_val),
        'total_deduct': "{:,.0f}".format(total_deduct),
        'base_bonus': "{:,.0f}".format(base_bonus),
        'sick_count': sick_count,
        'sick_deduct': "{:,.0f}".format(sick_count * 500),
        'business_count': business_count,
        'business_deduct': "{:,.0f}".format(business_count * 1000),
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
                try:
                    msg = f"🔔 มีคำขอลาใหม่!\nคุณ: {emp.first_name} {emp.last_name}\nประเภท: {leave.leave_type}\nวันที่: {leave.start_date} ถึง {leave.end_date}\nเหตุผล: {leave.reason}"
                    send_line_alert(msg)
                except: pass
                messages.success(request, 'ส่งใบลาเรียบร้อยแล้ว')
                return redirect('employee_detail', emp_id=emp.id)
            else:
                messages.error(request, 'ไม่พบข้อมูลพนักงาน')
    else:
        form = LeaveRequestForm()
    return render(request, 'employees/leave_form.html', {'form': form})

# ==========================================
# 4. ฟังก์ชันจัดการของ Admin
# ==========================================
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

    # 👇👇 ส่วนสำคัญ: ส่งไลน์กลับไปหาพนักงาน 👇👇
    try:
        # เช็คว่าพนักงานคนนี้มี Line User ID หรือยัง?
        if leave.employee.line_user_id:
            msg = f"✅ อนุมัติแล้ว!\n------------------\nถึง: {leave.employee.first_name}\nวันที่ลา: {leave.start_date}\n\nพักผ่อนให้เต็มที่นะครับ! 🏖️"
            # ส่งหาพนักงานโดยเฉพาะ (ระบุ ID ปลายทาง)
            send_line_alert(msg, leave.employee.line_user_id)
        else:
            print("⚠️ ไม่พบ Line User ID ของพนักงานคนนี้")
    except Exception as e:
        print(f"Error sending LINE: {e}")
    # 👆👆 ---------------------------------- 👆👆

    return redirect('dashboard')

@login_required
@user_passes_test(is_admin)
def reject_leave(request, leave_id):
    leave = get_object_or_404(LeaveRequest, pk=leave_id)
    leave.status = 'REJECTED'
    leave.save()

    # 👇👇 ส่วนสำคัญ: แจ้งผลปฏิเสธ 👇👇
    try:
        if leave.employee.line_user_id:
            msg = f"❌ ไม่อนุมัติ\n------------------\nถึง: {leave.employee.first_name}\nเหตุผล: งานเร่งด่วน\n\nโปรดติดต่อหัวหน้างานครับ"
            send_line_alert(msg, leave.employee.line_user_id)
    except: pass
    # 👆👆 ---------------------------------- 👆👆

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

# ==========================================
# 5. ฟังก์ชันอื่นๆ
# ==========================================
@login_required
def employee_payslip(request, emp_id):
    employee = get_object_or_404(Employee, pk=emp_id)
    salary = float(employee.base_allowance)
    sso_val = min(salary * 0.05, 750.0)
    total_income = salary
    net_salary = total_income - sso_val
    return render(request, 'employees/payslip.html', {
        'employee': employee,
        'salary': "{:,.2f}".format(salary),
        'total_income': "{:,.2f}".format(total_income),
        'sso': "{:,.2f}".format(sso_val),
        'net_salary': "{:,.2f}".format(net_salary),
        'today': timezone.now(),
    })

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

@login_required
def department_detail(request, dept_name):
    employees = Employee.objects.filter(department=dept_name)
    return render(request, 'employees/department_detail.html', {'dept_name': dept_name, 'employees': employees})

# ==========================================
# 6. Webhook (สำหรับจับปลาหา ID)
# ==========================================
@csrf_exempt
def line_webhook(request):
    if request.method == 'POST':
        try:
            payload = json.loads(request.body)
            print("🎣 Webhook ทำงาน! ข้อมูล:", payload)
            events = payload.get('events', [])
            for event in events:
                user_id = event.get('source', {}).get('userId')
                if user_id:
                    print(f"🎯 เจอตัวแล้ว! User ID คือ: {user_id}")
        except Exception as e:
            print(f"Webhook Error: {e}")
        return HttpResponse("OK", status=200)
    else:
        return HttpResponse("This is a webhook for LINE Bot.", status=200)

# ==========================================
# 7. หน้าจัดการผู้ใช้งาน (User Management)
# ==========================================
@login_required
@user_passes_test(is_admin)
def user_list(request):
    # ดึงข้อมูล User ทั้งหมดมาแสดง
    users = User.objects.all().order_by('id')
    return render(request, 'employees/user_list.html', {'users': users})

# ==========================================
# 8. ฟังก์ชันออกจากระบบ (Logout Custom)
# ==========================================
def logout_view(request):
    logout(request)
    return redirect('home')  # ออกแล้วเด้งกลับไปหน้า Login

# ==========================================
# 9. แอดมินรีเซ็ตรหัสผ่านให้ลูกน้อง
# ==========================================
@login_required
@user_passes_test(is_admin)
def admin_reset_password(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = SetPasswordForm(target_user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ เปลี่ยนรหัสผ่านของ {target_user.username} เรียบร้อยแล้ว!')
            return redirect('user_list')
    else:
        form = SetPasswordForm(target_user)

    return render(request, 'employees/password_reset.html', {
        'form': form,
        'target_user': target_user
    })