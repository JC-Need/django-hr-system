from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

# ✅ เพิ่ม 2 บรรทัดนี้: เพื่อเรียกการตั้งค่าและตัวจัดการไฟล์ Static/Media
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 1. หน้า Admin (ระบบหลังบ้าน)
    path('admin/', admin.site.urls),

    # 2. ระบบ Login
    path('accounts/login/', auth_views.LoginView.as_view(template_name='employees/login.html'), name='login'),

    # 3. ระบบ Logout (ออกแล้วเด้งกลับไปหน้า Login)
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # 4. เชื่อมโยงกับ App "employees" (หน้า Dashboard, ใบลา, ฯลฯ)
    path('', include('employees.urls')),
]

# ✅ เพิ่มส่วนนี้ต่อท้ายสุด: เพื่อให้เว็บ "มองเห็น" ไฟล์รูปภาพที่เราอัปโหลด
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)