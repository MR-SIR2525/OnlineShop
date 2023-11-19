import os
from decouple import config

BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

SECRET_KEY = config('SECRET_KEY')
#to avoid hard coding it in

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.humanize',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    
    'crispy_forms',
    'django_countries',
    'localflavor',

    'store'
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

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'backend.wsgi.application'

LANGUAGE_CODE = 'en-us'
# TIME_ZONE = 'UTC'
TIME_ZONE = 'America/Chicago'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static_in_env')]
STATIC_ROOT = os.path.join(BASE_DIR, 'static_root')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media_root')


#******************** ALLAUTH ********************
# setting AUTHENTICATION_BACKEND to allauth and keep default ModelBackend
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend'
)
SITE_ID = 1

# EMAIL_BACKEND so allauth can proceed to send confirmation emails
# --> ONLY for development/testing .console 
EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend'

# -----> Custom allauth settings
# Use email as the primary identifier
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True

#override allauth forms
ACCOUNT_FORMS = {'signup': 'store.forms.CustomSignupForm'}

# Eliminate need to provide username, as it's a very old practice
ACCOUNT_USERNAME_REQUIRED = False 

# ACCOUNT_EMAIL_VERIFICATION = 'mandatory' 
ACCOUNT_EMAIL_VERIFICATION = "none" #until I setup emails, this has to be none

#need to fix this later (looking at item, log in, then you've lost your train of thought and item)
LOGIN_REDIRECT_URL = '/'

#settings help: https://www.webforefront.com/django/usermanagementallauth.html)




#******************** CRISPY FORMS ********************
CRISPY_TEMPLATE_PACK = 'bootstrap4'
