from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.contrib.auth import login, logout
from django.db.models import Sum, Count
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Employee, Attendance, LeaveRequest, Product, Order, OrderItem
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
    except Exception as e:
        print(f"Line Error: {e}")

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
# 1. Dashboard (Timezone Fixed ✅)
# ==========================================
@login_required
def dashboard(request):
    if not request.user.is_superuser:
        emp = get_employee_from_user(request.user)
        if emp:
            return redirect('employee_detail', emp_id=emp.id)
        else:
            return render(request, 'employees/login.html', {'form': None, 'error': 'Access Denied'})

    # ✅ ใช้เวลาปัจจุบันตามโซน (ไทย)
    today = timezone.localtime(timezone.now()).date()

    # --- 🏢 ส่วนที่ 1: ข้อมูล HR ---
    total_employees = Employee.objects.count()
    total_salary = Employee.objects.aggregate(Sum('base_allowance'))['base_allowance__sum'] or 0
    pending_leaves = LeaveRequest.objects.filter(status='PENDING').count()
    present_count = Attendance.objects.filter(date=today).count()
    absent_today = total_employees - present_count

    # 1.1 กราฟคนมาทำงาน 7 วัน
    bar_labels = []
    bar_data = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        bar_labels.append(d.strftime('%d/%m'))
        bar_data.append(Attendance.objects.filter(date=d).count())

    # 1.2 กราฟวงกลม HR
    start_work_time = datetime.time(9, 0, 0)
    late_count = Attendance.objects.filter(date=today, time_in__gt=start_work_time).count()
    on_time_count = present_count - late_count

    # 1.3 งบแยกแผนก
    dept_summary = Employee.objects.values('department').annotate(
        count=Count('id'), total_salary=Sum('base_allowance')
    ).order_by('-total_salary')

    # --- 🔔 ส่วนที่ 3: กิจกรรมล่าสุด (Activity Feed) ---
    activities = []

    # 3.1 ดึงข้อมูลลงเวลา (Attendance)
    atts = Attendance.objects.filter(date=today).exclude(time_in__isnull=True)
    for a in atts:
        is_late = a.time_in > datetime.time(9, 0)
        status_text = "⚠️ มาสาย" if is_late else "✅ ปกติ"
        
        # ✅ แปลงเวลาให้เป็น Aware (มี Timezone) เพื่อให้ sort ได้
        naive_dt = datetime.datetime.combine(today, a.time_in)
        aware_dt = timezone.make_aware(naive_dt)

        activities.append({
            'timestamp': aware_dt,
            'time_show': a.time_in.strftime('%H:%M'),
            'icon': 'fa-fingerprint',
            'color': 'text-warning' if is_late else 'text-success',
            'bg': 'bg-warning-subtle' if is_late else 'bg-success-subtle',
            'title': f"{a.employee.first_name} ลงเวลาเข้างาน",
            'detail': f"สถานะ: {status_text}"
        })

    # 3.2 ดึงข้อมูลการลา (Leaves)
    leaves = LeaveRequest.objects.filter(created_at__date=today)
    for l in leaves:
        activities.append({
            'timestamp': l.created_at,
            'time_show': timezone.localtime(l.created_at).strftime('%H:%M'),
            'icon': 'fa-envelope-open-text',
            'color': 'text-primary',
            'bg': 'bg-primary-subtle',
            'title': f"{l.employee.first_name} ขอลา{l.get_leave_type_display()}",
            'detail': f"เหตุผล: {l.reason[:20]}..."
        })

    # 3.3 ดึงข้อมูลการขาย (POS Orders)
    orders = Order.objects.filter(order_date__date=today)
    for o in orders:
        activities.append({
            'timestamp': o.order_date,
            'time_show': timezone.localtime(o.order_date).strftime('%H:%M'),
            'icon': 'fa-cash-register',
            'color': 'text-info',
            'bg': 'bg-info-subtle',
            'title': f"{o.employee.first_name} ขายสินค้า (POS)",
            'detail': f"💰 ยอดเงิน: ฿{o.total_amount:,.2f}"
        })

    # 3.4 เรียงลำดับตามเวลา (ล่าสุดขึ้นก่อน)
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    activities = activities[:10]

    # --- 💰 ส่วนที่ 2: ข้อมูลยอดขาย (Sales Report) ---
    sales_today = Order.objects.filter(order_date__date=today).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    sales_month = Order.objects.filter(order_date__month=today.month, order_date__year=today.year).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    sales_chart_data = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        val = Order.objects.filter(order_date__date=d).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        sales_chart_data.append(float(val))

    top_products = OrderItem.objects.values('product__name').annotate(
        total_qty=Sum('quantity')
    ).order_by('-total_qty')[:5]
    top_prod_labels = [item['product__name'] for item in top_products]
    top_prod_data = [item['total_qty'] for item in top_products]

    context = {
        'total_employees': total_employees,
        'total_salary': "{:,.2f}".format(total_salary),
        'pending_leaves': pending_leaves,
        'absent_today': absent_today,
        'bar_labels': json.dumps(bar_labels),
        'bar_data': json.dumps(bar_data),
        'pie_data': json.dumps([on_time_count, late_count, absent_today]),
        'dept_summary': dept_summary,
        'activities': activities,
        'sales_today': "{:,.2f}".format(sales_today),
        'sales_month': "{:,.2f}".format(sales_month),
        'sales_chart_data': json.dumps(sales_chart_data),
        'top_prod_labels': json.dumps(top_prod_labels),
        'top_prod_data': json.dumps(top_prod_data),
    }
    return render(request, 'employees/dashboard.html', context)

# ==========================================
# 2. หน้าประวัติพนักงาน
# ==========================================
@login_required
def employee_detail(request, emp_id):
    employee = get_object_or_404(Employee, pk=emp_id)
    attendance_list = Attendance.objects.filter(employee=employee).order_by('-date')
    leave_list = LeaveRequest.objects.filter(employee=employee).order_by('-start_date')

    # กรองวันที่
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        attendance_list = attendance_list.filter(date__range=[start_date, end_date])
        leave_list = leave_list.filter(start_date__gte=start_date, start_date__lte=end_date)

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
    try:
        if leave.employee.line_user_id:
            msg = f"✅ อนุมัติแล้ว!\n------------------\nถึง: {leave.employee.first_name}\nวันที่ลา: {leave.start_date}"
            send_line_alert(msg, leave.employee.line_user_id)
    except: pass
    return redirect('dashboard')

@login_required
@user_passes_test(is_admin)
def reject_leave(request, leave_id):
    leave = get_object_or_404(LeaveRequest, pk=leave_id)
    leave.status = 'REJECTED'
    leave.save()
    try:
        if leave.employee.line_user_id:
            msg = f"❌ ไม่อนุมัติ\n------------------\nถึง: {leave.employee.first_name}\nโปรดติดต่อหัวหน้างาน"
            send_line_alert(msg, leave.employee.line_user_id)
    except: pass
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

# ✅ แก้ไขฟังก์ชันนี้ให้แปลงเวลาเป็น Local Time (ไทย)
@login_required
def attendance_action(request, emp_id):
    employee = get_object_or_404(Employee, pk=emp_id)
    
    # 🕒 แปลงเวลาเป็น Local Time (Asia/Bangkok)
    now_local = timezone.localtime(timezone.now())
    today = now_local.date()
    now_time = now_local.time()
    
    attendance, created = Attendance.objects.get_or_create(employee=employee, date=today)
    
    if not attendance.time_in:
        attendance.time_in = now_time # บันทึกเวลาไทย
    elif not attendance.time_out:
        attendance.time_out = now_time # บันทึกเวลาไทย
        
    attendance.save()
    return redirect('employee_detail', emp_id=emp_id)

@login_required
def department_detail(request, dept_name):
    employees = Employee.objects.filter(department=dept_name)
    return render(request, 'employees/department_detail.html', {'dept_name': dept_name, 'employees': employees})

# ==========================================
# 6. Webhook
# ==========================================
@csrf_exempt
def line_webhook(request):
    if request.method == 'POST':
        try:
            payload = json.loads(request.body)
            print("Webhook Payload:", payload)
        except: pass
        return HttpResponse("OK", status=200)
    return HttpResponse("Line Webhook", status=200)

# ==========================================
# 7. User Management
# ==========================================
@login_required
@user_passes_test(is_admin)
def user_list(request):
    users = User.objects.all().order_by('id')
    return render(request, 'employees/user_list.html', {'users': users})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
@user_passes_test(is_admin)
def admin_reset_password(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = SetPasswordForm(target_user, request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = SetPasswordForm(target_user)
    return render(request, 'employees/password_reset.html', {'form': form, 'target_user': target_user})

# ==========================================
# 🛒 8. ระบบ POS
# ==========================================
@login_required
def pos_home(request):
    products = Product.objects.filter(is_active=True, stock__gt=0)
    return render(request, 'employees/pos.html', {'products': products})

@login_required
def pos_checkout(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cart = data.get('cart', [])
            total_amount = data.get('total_amount', 0)
            emp = get_employee_from_user(request.user)
            order = Order.objects.create(employee=emp, total_amount=total_amount)
            for item in cart:
                product = Product.objects.get(id=item['id'])
                quantity = item['quantity']
                if product.stock >= quantity:
                    OrderItem.objects.create(order=order, product=product, quantity=quantity, price=product.price)
                    product.stock -= quantity
                    product.save()
            return JsonResponse({'success': True, 'order_id': order.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid Request'})