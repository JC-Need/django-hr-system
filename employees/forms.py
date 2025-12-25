from django import forms
from .models import LeaveRequest

class LeaveRequestForm(forms.ModelForm):
    # ✅ กำหนดฟิลด์วันที่ใหม่ เพื่อรองรับ dd/mm/yyyy และใส่คลาส 'datepicker'
    start_date = forms.DateField(
        label='ลาตั้งแต่วันที่',
        input_formats=['%d/%m/%Y'], # บอกระบบว่ารับค่าแบบ วัน/เดือน/ปี
        widget=forms.DateInput(attrs={
            'class': 'form-control datepicker', # ใส่ชื่อเล่นให้มันว่า datepicker
            'placeholder': 'วว/ดด/ปปปป'
        })
    )
    end_date = forms.DateField(
        label='ถึงวันที่',
        input_formats=['%d/%m/%Y'],
        widget=forms.DateInput(attrs={
            'class': 'form-control datepicker',
            'placeholder': 'วว/ดด/ปปปป'
        })
    )

    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'leave_type': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'เช่น ไม่สบาย, ไปทำธุระ...'}),
        }
        labels = {
            'leave_type': 'ประเภทการลา',
            'reason': 'เหตุผลการลา',
        }