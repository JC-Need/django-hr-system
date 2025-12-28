"""
Django settings for mycompany project.
"""

import os  # ✅ เติมอันนี้มาให้แล้วครับ
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
SECRET_KEY = 'django-insecure-change-this-key-to-something-secure'

DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'employees',
    'django.contrib.humanize',
    'import_export',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mycompany.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mycompany.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'JCNeed1975$hr_db',    # 👈 ชื่อ Database เต็มๆ (ที่มี $ คั่น)
        'USER': 'JCNeed1975',          # 👈 Username ของคุณ
        'PASSWORD': 'HrSystem2025',     # 👈 ⚠️ แก้ตรงนี้! ใส่รหัสผ่าน Database ที่ตั้งในข้อ 1
        'HOST': 'JCNeed1975.mysql.pythonanywhere-services.com', # 👈 Database host (อันยาวๆ)
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = []

# Internationalization
LANGUAGE_CODE = 'th'
TIME_ZONE = 'Asia/Bangkok'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'  # ✅ แก้เป็น /static/ (มี / ข้างหน้า)

# ✅ เติมบรรทัดสำคัญนี้ลงไป!
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==========================================
# ตั้งค่าการล็อกอิน/ล็อกเอาท์
# ==========================================
# ถ้ายังไม่ล็อกอิน ให้ดีดมาที่หน้าแรก (Home)
LOGIN_URL = '/'

# พอล็อกอินเสร็จ ให้ไป Dashboard
LOGIN_REDIRECT_URL = 'dashboard'

# พอล็อกเอาท์เสร็จ ให้กลับมาหน้าแรก (Home) 👈 ตัวนี้แหละครับที่ช่วยแก้ปัญหา
LOGOUT_REDIRECT_URL = '/'
# ==========================================
# ตั้งค่าการเก็บไฟล์รูปภาพ (Media)
# ==========================================
import os

# URL ที่ใช้เรียกดูรูปในหน้าเว็บ
MEDIA_URL = '/media/'

# โฟลเดอร์จริงๆ ในเครื่องที่จะเก็บไฟล์
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')