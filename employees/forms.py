from django import forms
from .models import Employee

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        # เลือกหัวข้อที่จะให้กรอก (ชื่อ, ตำแหน่ง, เงินเดือน, ตัวคูณ)
        fields = ['name', 'position', 'base_allowance', 'level_weight']
        
        # แต่งหน้าตาช่องกรอกข้อมูลให้ดูแพง (ใส่ CSS Class)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input-luxury', 'placeholder': 'ชื่อ-นามสกุล'}),
            'position': forms.TextInput(attrs={'class': 'input-luxury', 'placeholder': 'ตำแหน่ง (เช่น Manager)'}),
            'base_allowance': forms.NumberInput(attrs={'class': 'input-luxury', 'placeholder': 'เงินเดือน'}),
            'level_weight': forms.NumberInput(attrs={'class': 'input-luxury', 'placeholder': 'ตัวคูณ (Weight)'}),
        }