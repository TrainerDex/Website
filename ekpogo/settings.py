# -*- coding: utf-8 -*-
import os
import datetime

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '***REMOVED***'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

ADMINS = [('Jay Turner', 'jaynicholasturner@gmail.com')]

# Application definition

INSTALLED_APPS = [
    'flat_responsive',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.gis',
    'django_gravatar',
    'debug_toolbar',
    'rest_framework',
    'rest_framework.authtoken',
    'ajax_select',
    'cities',
    'colorful',
    'cookielaw',
    'rosetta',
    'trainer',
    'website',
    'support',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.discord',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.reddit',
    'allauth.socialaccount.providers.twitter',
    'allauth.socialaccount.providers.patreon',
    'allauth.socialaccount.providers.google',
    'widget_tweaks',
    'admin_reorder',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'admin_reorder.middleware.ModelAdminReorder',
]

LOCALE_PATHS = [
    'conf/locale',
]

ROOT_URLCONF = 'ekpogo.urls'

ADMIN_REORDER = (
    {'app': 'auth', 'models': ('auth.User', 'auth.Group', 'account.EmailAddress', 'authtoken.Token')},
    {'app': 'trainer', 'models': ('trainer.Trainer', 'trainer.Update', 'trainer.TrainerReport', 'trainer.Faction')},
    'socialaccount',
    'sites',
    'cities',
)
    
INTERNAL_IPS = [
    '127.0.0.1'
]
    
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
                'website.context_processors.google_analytics',
            ],
        },
    },
]

WSGI_APPLICATION = 'ekpogo.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'ekpogo',
        'USER': 'ekpogo',
        'PASSWORD': '***REMOVED***',
    }
}

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
USE_X_FORWARDED_HOST = True
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Django Rest Framework
# http://www.django-rest-framework.org/tutorial/4-authentication-and-permissions/

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        ),
    'DEFAULT_PERMISSION_CLASSES': (
        'ekpogo.permissions.IsAdminUserOrReadOnly',
        ),
}

# Django AllAuth
# http://django-allauth.readthedocs.io/en/latest/configuration.html

SITE_ID = 1

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_PRESERVE_USERNAME_CASING = True
ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE = True
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_USERNAME_VALIDATORS = 'trainer.validators.username_validator'
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)
LOGIN_REDIRECT_URL = 'profile'
SOCIALACCOUNT_AUTO_SIGNUP = False
SOCIALACCOUNT_PROVIDERS = {
    'reddit': {
        'AUTH_PARAMS': {'duration': 'permanent'},
        'SCOPE': ['identity', 'submit'],
        'USER_AGENT': 'django:trainerdex:1.0 (by /u/jayturnr)',
    },
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}
SOCIALACCOUNT_QUERY_EMAIL= True

# Google Analytics

GOOGLE_ANALYTICS_DOMAIN = 'trainerdex.co.uk'
GOOGLE_ANALYTICS_PROPERTY_ID = '***REMOVED***'

# Django Cities
# https://github.com/coderholic/django-cities#configuration

CITIES_LOCALES = ['en', 'da', 'de', 'es', 'fr', 'ja', 'nl', 'no', 'pl', 'sv']
CITIES_POSTAL_CODES = []

# Django Gravatar 2
# https://github.com/twaddington/django-gravatar/#configuring

GRAVATAR_DEFAULT_IMAGE = 'retro'
GRAVATAR_DEFAULT_RATING = 'g'

# Email
# https://docs.djangoproject.com/en/1.11/topics/email/

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'jaynicholasturner@gmail.com'
EMAIL_HOST_PASSWORD = 'vaxtomtayxewsqma'
DEFAULT_FROM_EMAIL = 'TrainerDex Support <support@trainerdex.co.uk>'
SERVER_EMAIL = DEFAULT_FROM_EMAIL
