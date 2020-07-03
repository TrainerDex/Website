import os

from django.utils.translation import gettext_lazy as _
from config import local_settings

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = local_settings.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = local_settings.DEBUG

ALLOWED_HOSTS = ['*']

ADMINS = local_settings.ADMINS

# Application definition

# django-cors-headers
# https://pypi.org/project/django-cors-headers/
# I read somewhere this has to be before django.contrib.sites

INSTALLED_APPS = [
    'corsheaders',
]

# django apps
# https://docs.djangoproject.com/en/3.0/

INSTALLED_APPS += [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.gis',
]

# django-rest-framework
# https://www.django-rest-framework.org/#installation

INSTALLED_APPS += [
    'rest_framework',
    'rest_framework.authtoken',
]

# first-party apps

INSTALLED_APPS += [
    # 'community',
    'core',
    'trainerdex',
]

# django-allauth
# https://django-allauth.readthedocs.io/en/stable/installation.html

INSTALLED_APPS += [
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.discord',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.twitter',
    ]

# other third-party apps

INSTALLED_APPS += [
    'django_countries',
    ]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ORIGIN_ALLOW_ALL = DEBUG

LOCALE_PATHS = [
    'config/locale',
]

ROOT_URLCONF = 'config.urls'

# DjangoDebugToolbar
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html

if DEBUG:
    if 'django.contrib.staticfiles' not in INSTALLED_APPS:
        INSTALLED_APPS.append('django.contrib.staticfiles')
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')
    INTERNAL_IPS = ['127.0.0.1']

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
                'core.context_processors.google_analytics',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
# Some settings handled in config.local_settings

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'django',
        'USER': local_settings.db_user,
        'PASSWORD': local_settings.db_password,
        'HOST': '127.0.0.1',
    }
}

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Custom user ModelBackend
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-user-model

AUTH_USER_MODEL = 'core.User'


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en'
LANGUAGES = [
    ('en', _('English')),
    ('de', _('German')),
    ('es', _('Spanish')),
    ('fr', _('French')),
    ('it', _('Italian')),
    ('ja', _('Japanese')),
    ('ko', _('Korean')),
    ('pt-br', _('Brazilian Portuguese')),
    ('zh-hant', _('Traditional Chinese')),
]

TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
if not DEBUG:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
USE_X_FORWARDED_HOST = True
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# CORS
# https://github.com/ottoyiu/django-cors-headers

CORS_ORIGIN_ALLOW_ALL = True

# Django Rest Framework
# http://www.django-rest-framework.org/tutorial/4-authentication-and-permissions/

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        ),
    'DEFAULT_PERMISSION_CLASSES': (
        'config.permissions.IsAdminUserOrReadOnly',
        ),
}

# Django AllAuth
# http://django-allauth.readthedocs.io/en/latest/configuration.html

SITE_ID = 1

ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_PRESERVE_USERNAME_CASING = True
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_USERNAME_MIN_LENGTH = 3
ACCOUNT_USERNAME_REQUIRED = True
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)
LOGIN_REDIRECT_URL = 'trainerdex:profile'
SOCIALACCOUNT_AUTO_SIGNUP = False
SOCIALACCOUNT_PROVIDERS = {
    'discord': {
        'SCOPE': [
            'identify',
            'email',
            'guilds',
            'guilds.join',
            'gdm.join',
        ]
    },
    'facebook': {
        'SCOPE': [
            'public_profile',
            'email',
            'user_location',
        ],
        'FIELDS': [
            'id',
            'email',
            'first_name',
            'last_name',
        ],
    },
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    },
}
SOCIALACCOUNT_QUERY_EMAIL = True

# Email
# https://docs.djangoproject.com/en/3.0/topics/email/

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = local_settings.EMAIL_HOST
EMAIL_USE_TLS = local_settings.EMAIL_USE_TLS
EMAIL_PORT = local_settings.EMAIL_PORT
EMAIL_HOST_USER = local_settings.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = local_settings.EMAIL_HOST_PASSWORD
DEFAULT_FROM_EMAIL = local_settings.DEFAULT_FROM_EMAIL
SERVER_EMAIL = DEFAULT_FROM_EMAIL

FILE_UPLOAD_PERMISSIONS = 0x775
