from django.contrib import admin
from .models import Employee, Attendance, LeaveRequest

# ปรับแต่งหน้า Admin ของพนักงาน
class EmployeeAdmin(admin.ModelAdmin):
    # ✅ เปลี่ยนจาก 'name' เป็น 'first_name' และ 'last_name'
    list_display = ('employee_id', 'first_name', 'last_name', 'position', 'department', 'status')
    search_fields = ('first_name', 'last_name', 'employee_id')
    list_filter = ('department', 'status')

# ปรับแต่งหน้า Admin ของการตอกบัตร
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'time_in', 'time_out')
    list_filter = ('date', 'employee')

# ปรับแต่งหน้า Admin ของการลา
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'leave_type')

# ลงทะเบียนเข้าสู่ระบบ Admin
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(LeaveRequest, LeaveRequestAdmin)