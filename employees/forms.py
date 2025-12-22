from django import forms
from .models import Employee, LeaveRequest  # เพิ่ม LeaveRequest เข้ามาตรงนี้

# 1. ฟอร์มพนักงาน (ของเดิม)
class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name', 'position', 'base_allowance', 'level_weight']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input-luxury', 'placeholder': 'ชื่อ-นามสกุล'}),
            'position': forms.TextInput(attrs={'class': 'input-luxury', 'placeholder': 'ตำแหน่ง'}),
            'base_allowance': forms.NumberInput(attrs={'class': 'input-luxury', 'placeholder': 'เงินเดือน'}),
            'level_weight': forms.NumberInput(attrs={'class': 'input-luxury', 'placeholder': 'ตัวคูณ'}),
        }

# 2. ฟอร์มใบลา (ของใหม่ที่เพิ่มเข้าไป)
class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['employee', 'leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'style': 'padding: 8px; border-radius: 4px; border: 1px solid #ccc;'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'style': 'padding: 8px; border-radius: 4px; border: 1px solid #ccc;'}),
            'reason': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'style': 'width: 100%; padding: 8px;'}),
        }