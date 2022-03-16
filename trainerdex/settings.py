import os

from django.core.management.utils import get_random_secret_key
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy

from trainerdex import __version__

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", get_random_secret_key())

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(int(os.environ.get("DEBUG", 0)))

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost").split(" ")
ALLOWED_CIDR_NETS = ["10.244.0.0/16"]

ADMINS = [("Jay Turner", "jaynicholasturner@gmail.com")]

# Application definition

INSTALLED_APPS = [
    "corsheaders",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.humanize",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.sitemaps",
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
    "silk.middleware.SilkyMiddleware",
    "allow_cidr.middleware.AllowCIDRMiddleware",
]

LOCALE_PATHS = [
    "trainerdex/locale",
]

ROOT_URLCONF = "trainerdex.urls"

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
                "trainerdex.context_processors.version",
            ],
        },
    },
]

WSGI_APPLICATION = "trainerdex.wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("SQL_ENGINE", "django.db.backends.postgresql"),
        "NAME": os.environ.get("SQL_DATABASE", "tdx"),
        "USER": os.environ.get("SQL_USER", "tdx"),
        "PASSWORD": os.environ.get("SQL_PASSWORD", "password"),
        "HOST": os.environ.get("SQL_HOST", "localhost"),
        "PORT": os.environ.get("SQL_PORT", "5432"),
    }
}

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

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

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_URL = "/static/"

# CORS
# https://github.com/ottoyiu/django-cors-headers

CORS_ORIGIN_ALLOW_ALL = True

# Django Rest Framework
# http://www.django-rest-framework.org/tutorial/4-authentication-and-permissions/

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework.authentication.TokenAuthentication",),
    "DEFAULT_PERMISSION_CLASSES": ("trainerdex.permissions.IsAdminUserOrReadOnly",),
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
    "discord": {"SCOPE": ["identify", "email", "guilds", "guilds.join", "gdm.join"]},
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
DISCORD_CLIENT_ID = int(os.environ.get("DISCORD_CLIENT_ID", "0"))
DISCORD_CLIENT_SECRET = os.environ.get("DISCORD_CLIENT_SECRET", "")
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
SILKY_META = True
