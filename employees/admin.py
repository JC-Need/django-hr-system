from django.contrib import admin
from django.utils.html import format_html
from .models import Employee, Attendance, LeaveRequest, Product, Order, OrderItem

# ============================================
# 1. ส่วนจัดการ HR
# ============================================

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'first_name', 'last_name', 'position', 'department', 'status')
    search_fields = ('first_name', 'last_name', 'employee_id')
    list_filter = ('department', 'status')

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'time_in', 'time_out')
    list_filter = ('date', 'employee')

class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'leave_type')

# ============================================
# 2. ส่วนจัดการ POS (ขายหน้าร้าน)
# ============================================

class ProductAdmin(admin.ModelAdmin):
    list_display = ('show_image', 'name', 'price', 'stock', 'is_active')
    search_fields = ('name',)
    list_editable = ('price', 'stock', 'is_active')
    list_filter = ('is_active',)

    # ✅ แก้ไขตรงนี้: ใส่ try-except ป้องกันเว็บล่ม
    def show_image(self, obj):
        try:
            if obj.image:
                return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px; border: 1px solid #ddd;" />', obj.image.url)
        except ValueError:
            pass  # ถ้าหาไฟล์ไม่เจอ ให้ข้ามไปทำงานบรรทัดล่าง
        
        return format_html('<span style="color: #ccc; font-size: 0.8em;">❌ ไม่มีรูป</span>')

    show_image.short_description = 'รูปตัวอย่าง'

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')
    can_delete = False

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'total_amount', 'order_date')
    list_filter = ('order_date', 'employee')
    inlines = [OrderItemInline]
    readonly_fields = ('total_amount', 'order_date')

# ============================================
# 3. ลงทะเบียน
# ============================================
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(LeaveRequest, LeaveRequestAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)