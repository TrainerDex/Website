import os
from distutils.util import strtobool
from pathlib import Path

from django.core.management.utils import get_random_secret_key
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy

from config import __version__

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

SECRET_KEY = os.environ.get("SECRET_KEY", get_random_secret_key())

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = strtobool(os.environ.get("DEBUG", "False"))

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost").split(" ")
ALLOWED_CIDR_NETS = ["10.244.0.0/16"]

ADMINS = [("Jay Turner", "jaynicholasturner@gmail.com")]

# Application definition

INSTALLED_APPS = [
    "corsheaders",
    "django.contrib.admin",
    "django.contrib.admindocs",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.humanize",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "django.contrib.postgres",
    "psqlextra",
    "rest_framework",
    "rest_framework.authtoken",
    "silk",
    "core",
    "pokemongo",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.discord",
    "allauth.socialaccount.providers.reddit",
    "allauth.socialaccount.providers.twitter",
    "widget_tweaks",
    "robots",
    "oauth2_provider",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.admindocs.middleware.XViewMiddleware",
    "silk.middleware.SilkyMiddleware",
    "allow_cidr.middleware.AllowCIDRMiddleware",
]

LOCALE_PATHS = [
    "config/locale",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.google_analytics",
                "config.context_processors.version",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "psqlextra.backend",
        "NAME": os.environ.get("SQL_DATABASE", "trainerdex"),
        "USER": os.environ.get("SQL_USER", "trainerdex"),
        "PASSWORD": os.environ.get("SQL_PASSWORD", "password"),
        "HOST": os.environ.get("SQL_HOST", "localhost"),
        "PORT": os.environ.get("SQL_PORT", "5432"),
    }
}

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-US"
LANGUAGES = [
    ("de-DE", _("German")),
    ("en-US", _("English")),
    ("es-ES", _("Spanish")),
    ("fr-FR", _("French")),
    ("it-IT", _("Italian")),
    ("ja-JP", _("Japanese")),
    ("ko-KR", _("Korean")),
    ("nl-NL", _("Dutch")),
    ("nl-BE", _("Dutch, Belgium")),
    ("ro-RO", _("Romanian")),
    ("ru-RU", _("Russian")),
    ("pt-BR", _("Brazilian Portuguese")),
    ("th-TH", _("Thai")),
    ("zh-HK", _("Traditional Chinese")),
]

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_URL = "/static/"


# CORS
# https://github.com/ottoyiu/django-cors-headers

CORS_ALLOW_ALL_ORIGINS = True
CSRF_TRUSTED_ORIGINS = ["https://trainerdex.app", "https://beta.trainerdex.app"]

# Django Rest Framework
# http://www.django-rest-framework.org/tutorial/4-authentication-and-permissions/

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
        "oauth2_provider.contrib.rest_framework.OAuth2Authentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("core.permissions.IsStaffOrReadOnly",),
    # "DEFAULT_RENDERER_CLASSES": ("drf_ujson.renderers.UJSONRenderer",),
    # "DEFAULT_PARSER_CLASSES": ("drf_ujson.parsers.UJSONParser",),
    "COERCE_DECIMAL_TO_STRING": False,
    "PAGE_SIZE": 50,
}

# Django OAuth Toolkit
# https://django-oauth-toolkit.readthedocs.io/en/2.0.0/settings.html

OAUTH2_PROVIDER = {
    "SCOPES": {
        "read": "Read Trainer profile and Updates",
        "write": "Edit Trainer profile and Updates",
        "delete:updates": "Delete Updates",
        "read:social": "Read social accounts",
        "write:social": "Write social accounts",
    },
    "DEFAULT_SCOPES": ["read"],
}

# Django AllAuth
# http://django-allauth.readthedocs.io/en/latest/configuration.html

SITE_ID = 1

ACCOUNT_ADAPTER = "core.account_adapter.NoNewUsersAccountAdapter"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_PRESERVE_USERNAME_CASING = True
ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE = True
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_USERNAME_VALIDATORS = "pokemongo.validators.username_validator"
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)
LOGIN_REDIRECT_URL = "trainerdex:profile"
SOCIALACCOUNT_AUTO_SIGNUP = False
SOCIALACCOUNT_PROVIDERS = {
    "reddit": {
        "AUTH_PARAMS": {"duration": "permanent"},
        "SCOPE": ["identity", "submit"],
        "USER_AGENT": f"django:trainerdex:{__version__} (by /u/jayturnr)",
    },
    "google": {"SCOPE": ["profile", "email"], "AUTH_PARAMS": {"access_type": "online"}},
    "discord": {"SCOPE": ["identify", "email", "guilds", "guilds.join", "guilds.members.read"]},
}
SOCIALACCOUNT_QUERY_EMAIL = True

# Google Analytics

GOOGLE_ANALYTICS_MEASUREMENT_ID = os.environ.get("GOOGLE_ANALYTICS_MEASUREMENT_ID", "")

# Email
# https://docs.djangoproject.com/en/2.2/topics/email/

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.eu.mailgun.org")
EMAIL_USE_TLS = bool(int(os.environ.get("EMAIL_USE_TLS", 1)))
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "postmaster@mmg.trainerdex.app")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "password")
DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL", "TrainerDex Support <jay@trainerdex.app>"
)
SERVER_EMAIL = DEFAULT_FROM_EMAIL

FILE_UPLOAD_PERMISSIONS = 0x775

# DISCORD
# Could this be stored in the database?
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN", "")

# CONSTANTS
# This should defo me stored elsewhere
TEAMS = {
    0: pgettext_lazy("team_name_team0", "No Team"),
    1: pgettext_lazy("team_name_team1", "Team Mystic"),
    2: pgettext_lazy("team_name_team2", "Team Valor"),
    3: pgettext_lazy("team_name_team3", "Team Instinct"),
}

SILKY_AUTHENTICATION = True  # User must login
SILKY_AUTHORISATION = True  # User must have permissions
SILKY_IGNORE_PATHS = [
    "/api/health/",  # DigitalOcean calls this every 10 seconds, let's exclude that.
    "/favicon.ico",
]
SILKY_META = True


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
