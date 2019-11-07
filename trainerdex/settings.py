# -*- coding: utf-8 -*-
import os
from django.utils.translation import gettext_lazy as _, pgettext_lazy

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '***REMOVED***'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

ADMINS = [('Jay Turner', 'jaynicholasturner@gmail.com')]

# Application definition

INSTALLED_APPS = [
    'corsheaders',
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
    'django_unused_media',
    'rest_framework',
    'rest_framework.authtoken',
    'cities',
    'cookielaw',
    'rosetta',
    'core',
    'pokemongo',
    'discordbot',
    ]

INSTALLED_APPS += [
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.discord',
    'allauth.socialaccount.providers.reddit',
    'allauth.socialaccount.providers.twitter',
    ]

INSTALLED_APPS += [
    'widget_tweaks',
    ]

INSTALLED_APPS += [
    'markdown_deux',
    'bootstrapform',
    'helpdesk',
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

LOCALE_PATHS = [
    'trainerdex/locale',
]

ROOT_URLCONF = 'trainerdex.urls'

# DjangoDebugToolbar
if DEBUG==True:
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

WSGI_APPLICATION = 'trainerdex.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'ekpogo',
        'USER': 'ekpogo',
        'PASSWORD': '***REMOVED***',
        'HOST': '127.0.0.1',
    }
}

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

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

ROSETTA_ENABLE_TRANSLATION_SUGGESTIONS = True
YANDEX_TRANSLATE_KEY = 'trnsl.1.1.20180810T220137Z.fc1ed7f844d35593.7750326807792ffa52d9d97276c6fab1cf66e178'
ROSETTA_POFILE_WRAP_WIDTH = 0
ROSETTA_SHOW_AT_ADMIN_PANEL = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
# if DEBUG:
    # STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
# else:
    # STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
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
        'trainerdex.permissions.IsAdminUserOrReadOnly',
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
ACCOUNT_USERNAME_VALIDATORS = 'pokemongo.validators.username_validator'
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)
LOGIN_REDIRECT_URL = 'trainerdex:profile'
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
    },
    'discord': {
        'SCOPE': [
            'identify',
            'email',
            'guilds',
            'guilds.join',
            'gdm.join',
        ]
    }
}
SOCIALACCOUNT_QUERY_EMAIL= True

# Google Analytics

GOOGLE_ANALYTICS_DOMAIN = 'trainerdex.co.uk'
GOOGLE_ANALYTICS_PROPERTY_ID = '***REMOVED***'

# Django Cities
# https://github.com/coderholic/django-cities#configuration

CITIES_LOCALES = ['LANGUAGES']
CITIES_POSTAL_CODES = []

# Email
# https://docs.djangoproject.com/en/2.1/topics/email/

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'noreply@mg.trainerdex.co.uk'
EMAIL_HOST_PASSWORD = '***REMOVED***'
DEFAULT_FROM_EMAIL = 'TrainerDex Support <jay@trainerdex.co.uk>'
SERVER_EMAIL = DEFAULT_FROM_EMAIL

FILE_UPLOAD_PERMISSIONS = 0x775

# Helpdesk

HELPDESK_USE_CDN = True
HELPDESK_TRANSLATE_TICKET_COMMENTS = True
HELPDESK_AUTO_SUBSCRIBE_ON_TICKET_RESPONSE = True
HELPDESK_STAFF_ONLY_TICKET_OWNERS = True
HELPDESK_STAFF_ONLY_TICKET_CC = True

# DISCORD

DISCORD_CLIENT_ID = ***REMOVED***
DISCORD_CLIENT_SECRET = '***REMOVED***'
DISCORD_TOKEN = '***REMOVED***'

# CONSTANTS

TEAMS = {
    0: pgettext_lazy(context="team_name_team0", message="No Team"),
    1: pgettext_lazy(context="team_name_team1", message="Team Mystic"),
    2: pgettext_lazy(context="team_name_team2", message="Team Valor"),
    3: pgettext_lazy(context="team_name_team3", message="Team Instinct"),
}
