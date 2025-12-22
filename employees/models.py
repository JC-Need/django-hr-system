from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User  # ✨ 1. นำเข้าโมเดล User ของระบบ

# 1. ข้อมูลพนักงาน
class Employee(models.Model):
    # ✨ 2. เชื่อม User เข้ากับ Employee (1 คน มีได้ 1 User เท่านั้น)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="บัญชีผู้ใช้งาน (User)")
    
    name = models.CharField(max_length=100, verbose_name="ชื่อ-นามสกุล")
    position = models.CharField(max_length=100, verbose_name="ตำแหน่ง")
    base_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="เงินเดือน")
    level_weight = models.DecimalField(max_digits=5, decimal_places=2, default=1.00, verbose_name="ตัวคูณโบนัส")
    
    emp_id = models.CharField(max_length=10, blank=True, null=True, verbose_name="รหัสพนักงาน")
    department = models.CharField(max_length=100, blank=True, null=True, verbose_name="แผนก")
    hire_date = models.DateField(default=timezone.now, verbose_name="วันที่เริ่มงาน")
    birth_date = models.DateField(blank=True, null=True, verbose_name="วันเกิด")
    resume_link = models.URLField(blank=True, null=True, verbose_name="🔗 ลิงก์ใบสมัคร/CV")

    STATUS_CHOICES = [
        ('ACTIVE', '✅ ทำงานอยู่ (Active)'),
        ('RESIGNED', '❌ ลาออกแล้ว (Resigned)'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE', verbose_name="สถานะการทำงาน")

    policy_doc_link = models.URLField(blank=True, null=True, verbose_name="🔗 ลิงก์ลายเซ็นรับทราบกฎระเบียบ")
    resignation_doc_link = models.URLField(blank=True, null=True, verbose_name="🔗 ลิงก์ใบลาออก (ถ้ามี)")

    bonus_amount = models.CharField(max_length=50, default="0.00")

    def __str__(self):
        return f"{self.name} ({self.position})"


# 2. ข้อมูลการลงเวลา
class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="ชื่อพนักงาน")
    date = models.DateField(default=timezone.now, verbose_name="วันที่")
    time_in = models.TimeField(blank=True, null=True, verbose_name="เวลาเข้างาน")
    time_out = models.TimeField(blank=True, null=True, verbose_name="เวลาออกงาน")
    
    def __str__(self):
        return f"{self.employee.name} - {self.date}"


# 3. ข้อมูลการลางาน
class LeaveRequest(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="ชื่อพนักงาน")
    
    LEAVE_TYPES = [
        ('SICK', '🤒 ลาป่วย (Sick Leave)'),
        ('VACATION', '🏖️ ลาพักร้อน (Vacation)'),
        ('BUSINESS', '💼 ลากิจ (Business Leave)'),
    ]
    leave_type = models.CharField(max_length=10, choices=LEAVE_TYPES, default='SICK', verbose_name="ประเภทการลา")
    
    start_date = models.DateField(verbose_name="ลาตั้งแต่วันที่")
    end_date = models.DateField(verbose_name="ถึงวันที่")
    reason = models.TextField(blank=True, null=True, verbose_name="เหตุผล")
    
    STATUS_CHOICES = [
        ('PENDING', '🟡 รออนุมัติ'),
        ('APPROVED', '🟢 อนุมัติแล้ว'),
        ('REJECTED', '🔴 ไม่อนุมัติ'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING', verbose_name="สถานะ")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="วันที่ยื่นใบลา")

    def __str__(self):
        return f"{self.employee.name} - {self.get_leave_type_display()}"