from django.db import models
from django.contrib.auth.models import User

# ================================
# 1. ตารางพนักงาน (Employee)
# ================================
class Employee(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'ทำงานอยู่'),
        ('PROBATION', 'ทดลองงาน'),
        ('RESIGNED', 'ลาออก'),
    ]

    # เชื่อมกับ User ของ Django
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    
    # ✅ ข้อมูลพื้นฐาน
    employee_id = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name="รหัสพนักงาน")
    first_name = models.CharField(max_length=100, verbose_name="ชื่อจริง", default="")
    last_name = models.CharField(max_length=100, verbose_name="นามสกุล", default="")
    
    # ✅ ช่องเก็บรูป (ใช้ชื่อตัวแปรว่า image ตามที่คุณตั้งไว้)
    image = models.ImageField(upload_to='employee_images/', blank=True, null=True, verbose_name="รูปโปรไฟล์")

    position = models.CharField(max_length=100, verbose_name="ตำแหน่ง")
    department = models.CharField(max_length=100, verbose_name="แผนก")
    
    # เงินๆ ทองๆ
    base_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=15000, verbose_name="เงินเดือน")
    bonus_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="โบนัสสะสม")
    
    # อื่นๆ
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE', verbose_name="สถานะ")
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="เบอร์โทร")
    joined_date = models.DateField(auto_now_add=True, verbose_name="วันที่เริ่มงาน")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.position})"

    @property
    def formatted_salary(self):
        return "{:,.2f}".format(self.base_allowance)

# ================================
# 2. ตารางตอกบัตร (Attendance)
# ================================
class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    time_in = models.TimeField(null=True, blank=True)
    time_out = models.TimeField(null=True, blank=True)

    class Meta:
        unique_together = ('employee', 'date')

    def __str__(self):
        return f"{self.employee.first_name} - {self.date}"

# ================================
# 3. ตารางการลา (Leave Request)
# ================================
class LeaveRequest(models.Model):
    LEAVE_TYPES = [
        ('SICK', 'ลาป่วย'),
        ('BUSINESS', 'ลากิจ'),
        ('VACATION', 'พักร้อน'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'รออนุมัติ'),
        ('APPROVED', 'อนุมัติ'),
        ('REJECTED', 'ไม่อนุมัติ'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.first_name} - {self.leave_type}"
    
    @property
    def days(self):
        delta = self.end_date - self.start_date
        return delta.days + 1