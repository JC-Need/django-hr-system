from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Employee, Attendance, LeaveRequest, Product, Order, OrderItem
from import_export.admin import ImportExportModelAdmin

# ==========================================
# 1. ปรับแต่ง User Admin (หน้ารายชื่อ User)
# ==========================================
class EmployeeInline(admin.StackedInline):
    model = Employee
    can_delete = False
    verbose_name_plural = 'Employee Info'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = (EmployeeInline, )
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_employee_status', 'is_staff')
    
    # ✅ เช็คสถานะแบบไม่สนตัวพิมพ์ (Active/active/ACTIVE ผ่านหมด)
    def get_employee_status(self, obj):
        if hasattr(obj, 'employee') and obj.employee:
            status = str(obj.employee.status).lower()
            return status == 'active' or status == 'ทำงานปกติ'
        return False
    
    get_employee_status.boolean = True
    get_employee_status.short_description = 'สถานะของพนักงาน'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# ==========================================
# 2. Employee Admin (จัดการพนักงาน)
# ==========================================
@admin.register(Employee)
class EmployeeAdmin(ImportExportModelAdmin):
    list_display = ('employee_id', 'first_name', 'last_name', 'department', 'position', 'status_show')
    search_fields = ('first_name', 'last_name', 'employee_id')
    list_filter = ('department', 'status')

    def status_show(self, obj):
        return obj.status
    status_show.short_description = 'สถานะ'

# ==========================================
# 3. Model อื่นๆ (ตัด Department ออกแล้ว)
# ==========================================
@admin.register(Attendance)
class AttendanceAdmin(ImportExportModelAdmin):
    list_display = ('employee', 'date', 'time_in', 'time_out')
    list_filter = ('date', 'employee__department')

@admin.register(LeaveRequest)
class LeaveRequestAdmin(ImportExportModelAdmin):
    list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'leave_type')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'is_active')
    list_editable = ('price', 'stock', 'is_active')
    search_fields = ('name',)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'total_amount', 'order_date')
    inlines = [OrderItemInline]
    readonly_fields = ('order_date',)