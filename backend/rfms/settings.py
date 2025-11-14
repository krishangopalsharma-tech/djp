from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-insecure-change-me")
DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "192.168.3.240", "192.168.3.230"]

INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "corsheaders",
    "django_extensions",
    "debug_toolbar",
    "django_filters",
    # Local apps
    "core.apps.CoreConfig",
    "users.apps.UsersConfig",
    "failures.apps.FailuresConfig",
    "operations.apps.OperationsConfig",
    "analytics.apps.AnalyticsConfig",
    # Refactored apps
    "archive.apps.ArchiveConfig",
    "circuits.apps.CircuitsConfig",
    "dashboard.apps.DashboardConfig",
    "depots.apps.DepotsConfig",
    "email_notifications.apps.EmailNotificationsConfig",
    "failure_config.apps.FailureConfigConfig",
    "logbook.apps.LogbookConfig",
    "recent_failures.apps.RecentFailuresConfig",
    "reports.apps.ReportsConfig",
    "sections.apps.SectionsConfig",
    "stations.apps.StationsConfig",
    "supervisors.apps.SupervisorsConfig",
    "telegram_notifications.apps.TelegramNotificationsConfig",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "rfms.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "rfms.wsgi.application"
ASGI_APPLICATION = "rfms.asgi.application"

# Dev DB: SQLite; we can switch to Postgres later via env
DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.getenv("DB_NAME", BASE_DIR / "db.sqlite3"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I1N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
}

# CORS / CSRF for Vite (adjust for prod later)
# We are temporarily allowing all origins for easier development debugging.
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# We keep the specific origins for CSRF protection
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://192.168.3.240:5173",
    "http://192.168.3.230:5173",
]

AUTH_USER_MODEL = 'users.User'

# Telegram Bot Token (IMPORTANT: Use environment variables in production!)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Base URL for the frontend application, used for generating links in notifications
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://192.168.3.230:5173")

INTERNAL_IPS = [
    "127.0.0.1",
    "192.168.3.111", # &lt;-- Add your computer's IP here
    "192.168.3.33",
    "192.168.3.230",
    "192.168.3.240", # &lt;-- ADD THIS LINE
]

# --- EMAIL CONFIGURATION ---
# These are the settings that Django's send_mail function will use.
# For a basic setup, you can hardcode them here.
# For a dynamic setup, you'd need a custom email backend
# that reads from the EmailSettings model.
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.example.com'  # Replace with your host
EMAIL_PORT = 587                   # Replace with your port
EMAIL_USE_TLS = True               # Use True for STARTTLS
EMAIL_USE_SSL = False              # Use True for SSL/TLS
EMAIL_HOST_USER = 'user@example.com' # Replace with your username
EMAIL_HOST_PASSWORD = 'your-password' # Replace with your password
