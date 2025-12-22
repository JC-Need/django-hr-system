from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import Template, RequestContext
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .models import Employee, Attendance, LeaveRequest
from .forms import LeaveRequestForm

# 1. หน้า Dashboard (Main Control Center)
@never_cache      # ห้ามจำหน้าเก่า (แก้ปัญหา Back แล้วยังเข้าได้)
@login_required   # ต้องล็อกอินก่อน
def dashboard(request):
    # --- A. ตรวจสอบตัวตน: User นี้คือพนักงานคนไหน? ---
    try:
        current_emp = request.user.employee
    except:
        # ถ้าบัญชียังไม่จับคู่ -> แสดงหน้า Error พร้อมปุ่ม Logout
        error_html = """
            <div style="text-align:center; margin-top:50px; font-family:sans-serif;">
                <h1 style="color:red;">⛔ บัญชีนี้ยังไม่ได้ผูกกับพนักงาน</h1>
                <p>โปรดติดต่อผู้ดูแลระบบ (Admin) เพื่อทำการจับคู่ User กับ Employee</p>
                <br>
                <form action="/logout/" method="post">
                    {% csrf_token %}
                    <button type="submit" style="background-color: #dc3545; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-size: 16px; font-weight: bold;">
                        🚪 ออกจากระบบ
                    </button>
                </form>
            </div>
        """
        return HttpResponse(Template(error_html).render(RequestContext(request)))

    # --- B. กฎการมองเห็น (Visibility Rules) 👁️ ---
    # แผนกที่มีสิทธิ์เห็นข้อมูลทุกคน (บอส และ HR)
    privileged_depts = ['Management', 'Human Resources'] 
    
    # เงื่อนไข: ถ้าอยู่แผนกพิเศษ หรือ เป็น Superuser -> ให้เห็นทั้งหมด (all)
    if current_emp.department in privileged_depts or request.user.is_superuser:
        employees = Employee.objects.all()
        is_manager = True
    else:
        # พนักงานทั่วไป -> เห็นแค่ตัวเองคนเดียว (filter id)
        employees = Employee.objects.filter(id=current_emp.id)
        is_manager = False

    # --- C. ระบบกรองแผนก (เฉพาะคนที่มีสิทธิ์เห็นหลายคน) ---
    department_list = []
    selected_dept = None
    
    if is_manager: 
        department_list = Employee.objects.values_list('department', flat=True).distinct()
        department_list = [d for d in department_list if d]
        selected_dept = request.GET.get('dept') 
        if selected_dept:
            employees = employees.filter(department=selected_dept)

    # --- D. วนลูปจัดการข้อมูลแสดงผล (เงินเดือน, ตอกบัตร) ---
    today = timezone.now().date()
    for emp in employees:
        emp.formatted_salary = "{:,.2f}".format(emp.base_allowance)
        attendance = Attendance.objects.filter(employee=emp, date=today).first()
        emp.today_attendance = attendance

    # --- E. ประวัติการลา (Leave History) ---
    if is_manager:
        # หัวหน้าเห็นใบลาของทุกคน (เรียงใหม่ -> เก่า)
        leaves = LeaveRequest.objects.all().order_by('-created_at')
    else:
        # พนักงานเห็นแค่ของตัวเอง
        leaves = LeaveRequest.objects.filter(employee=current_emp).order_by('-created_at')

    context = {
        'employees': employees,
        'department_list': department_list,
        'selected_dept': selected_dept,
        'leaves': leaves,
    }
    return render(request, 'employees/dashboard.html', context)


# 2. หน้าเขียนใบลา (Leave Request)
@never_cache
@login_required
def leave_request(request):
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            # เชื่อม User ที่ล็อกอิน เข้ากับใบลาอัตโนมัติ
            try:
                leave.employee = request.user.employee
                leave.save()
                return redirect('dashboard')
            except:
                return HttpResponse("Error: บัญชีของคุณยังไม่ได้ผูกกับพนักงาน")
    else:
        form = LeaveRequestForm()
    
    return render(request, 'employees/leave_form.html', {'form': form})


# 3. ฟังก์ชันตอกบัตร (Check-in/Out)
@login_required
def attendance_action(request, emp_id):
    target_emp = get_object_or_404(Employee, id=emp_id)
    
    # กฎ: ห้ามตอกบัตรให้คนอื่น (ยกเว้นเป็นบอส/Admin)
    privileged_depts = ['Management', 'Human Resources']
    
    # เช็คว่าคนกดคือใคร?
    try:
        requester = request.user.employee
        is_boss = (requester.department in privileged_depts)
    except:
        is_boss = False # ถ้าหาตัวคนกดไม่เจอ ตีว่าเป็นคนนอก

    # ถ้าไม่ใช่เจ้าของบัตร และไม่ใช่บอส และไม่ใช่ Superuser -> ดีดออก
    if request.user.employee != target_emp and not is_boss and not request.user.is_superuser:
        return redirect('dashboard') 

    # บันทึกเวลา
    today = timezone.now().date()
    attendance, created = Attendance.objects.get_or_create(employee=target_emp, date=today)

    if created:
        attendance.time_in = timezone.now().time()
        attendance.save()
    elif not attendance.time_out:
        attendance.time_out = timezone.now().time()
        attendance.save()
    
    return redirect('dashboard')


# 4. ฟังก์ชันคำนวณโบนัส
@login_required
def calculate_bonus(request):
    if request.method == "POST":
        # เช็คสิทธิ์: เฉพาะ Management/HR หรือ Superuser
        try:
            current_emp = request.user.employee
            if not request.user.is_superuser and current_emp.department not in ['Management', 'Human Resources']:
                 return redirect('dashboard')
        except:
             if not request.user.is_superuser: return redirect('dashboard')

        employees = Employee.objects.all()
        for emp in employees:
            try:
                salary = float(emp.base_allowance)
                weight = float(emp.level_weight)
                bonus = salary * weight
                emp.bonus_amount = "{:,.2f}".format(bonus)
                emp.save()
            except:
                continue
    return redirect('dashboard')


# 5. ฟังก์ชันลบพนักงาน
@login_required
def delete_employee(request, emp_id):
    # ให้เฉพาะ Superuser (Admin สูงสุด) ลบได้เท่านั้น
    if not request.user.is_superuser:
        return redirect('dashboard')
        
    emp = get_object_or_404(Employee, id=emp_id)
    emp.delete()
    return redirect('dashboard')