from django.contrib import admin
from .models import Employee, Attendance, LeaveRequest # เพิ่ม LeaveRequest

# 1. พนักงาน
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('emp_id', 'name', 'department', 'status', 'hire_date')
    list_filter = ('department', 'status')
    search_fields = ('name', 'emp_id')
    ordering = ('emp_id',)

# 2. ลงเวลา
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'time_in', 'time_out')
    list_filter = ('date', 'employee')
    date_hierarchy = 'date'

# 3. ใบลา (ของใหม่)
@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'leave_type', 'employee')
    list_editable = ('status',) # อนุญาตให้กดอนุมัติจากหน้าตารางได้เลย เร็วดี!