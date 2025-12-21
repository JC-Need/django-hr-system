from django.db import models

class Employee(models.Model):
    # --- 1. ข้อมูลส่วนตัว ---
    name = models.CharField(max_length=100, verbose_name="ชื่อ-นามสกุล")
    position = models.CharField(max_length=100, verbose_name="ตำแหน่ง")
    
    # --- 2. ข้อมูลเงินและตัวคูณ (ตามสูตร Waterfall) ---
    base_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="เงินประจำตำแหน่ง")
    level_weight = models.DecimalField(max_digits=4, decimal_places=2, default=1.0, verbose_name="ตัวคูณโบนัส")
    
    # --- 3. โครงสร้าง Tree (หัวหน้า-ลูกน้อง) ---
    manager = models.ForeignKey(
        'self',               # เชื่อมโยงหาตัวเอง (Self-referential)
        on_delete=models.SET_NULL, # ถ้าหัวหน้าออก ลูกน้องยังอยู่
        null=True,            # เป็น CEO ได้ (ไม่มีหัวหน้า)
        blank=True,
        related_name='subordinates', # ชื่อเล่นเอาไว้เรียกหาลูกน้อง
        verbose_name="หัวหน้างาน"
    )

    def __str__(self):
        return f"{self.name} ({self.position})"