"""Django settings for the SiBekas project."""

import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Environment variables supplied by the host take precedence over the local file.
load_dotenv(BASE_DIR / ".env")


def env_bool(name, default=False):
    """Read a boolean environment variable using common truthy values."""
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_list(name, default=""):
    """Read a comma-separated environment variable as a clean list."""
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


DEBUG = env_bool("DJANGO_DEBUG", default=True)
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-local-development-key-change-before-deploying",
)

if not DEBUG and SECRET_KEY.startswith("django-insecure-"):
    raise ImproperlyConfigured(
        "DJANGO_SECRET_KEY harus diatur ke nilai rahasia saat DJANGO_DEBUG=False."
    )

PWS_HOST = "faris-salman-sibekas.pws.cs.ui.ac.id"
PWS_ORIGIN = f"https://{PWS_HOST}"

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS")

# The PWS deployment URL is part of this application's public configuration.
# Keep it available even when the deployment has no environment variables yet.
if PWS_HOST not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(PWS_HOST)
if PWS_ORIGIN not in CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS.append(PWS_ORIGIN)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "product.apps.ProductConfig",
    "profiles.apps.ProfileConfig",
    "cart.apps.CartConfig",
    "order.apps.OrderConfig",
    "review.apps.ReviewConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "sibekas.urls"

LOGIN_URL = "profile:login"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = os.getenv("MAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("MAIL_PORT", "465"))

EMAIL_USE_TLS = False
EMAIL_USE_SSL = True

EMAIL_HOST_USER = os.getenv("MAIL_USERNAME", "")
EMAIL_HOST_PASSWORD = os.getenv("MAIL_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.getenv("MAIL_FROM_EMAIL") or EMAIL_HOST_USER

EMAIL_TIMEOUT = 15
PASSWORD_RESET_TIMEOUT = 3600

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "cart.context_processors.cart_count",
            ],
        },
    },
]

WSGI_APPLICATION = "sibekas.wsgi.application"
ASGI_APPLICATION = "sibekas.asgi.application"

DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=0 if DEBUG else 600,
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "id"
TIME_ZONE = "Asia/Jakarta"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
WHITENOISE_USE_FINDERS = True
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# RajaOngkir uses subdistrict IDs from its direct destination search.
# All parcels leave the configured SiBekas campus collection point.
RAJAONGKIR_API_KEY = os.getenv("RAJAONGKIR_API_KEY", "")
RAJAONGKIR_ORIGIN_ID = os.getenv("RAJAONGKIR_ORIGIN_ID", "")
RAJAONGKIR_COURIERS = os.getenv("RAJAONGKIR_COURIERS", "jne:jnt:sicepat")
ORDER_ENABLE_DEMO_PAYMENT = env_bool("ORDER_ENABLE_DEMO_PAYMENT", default=DEBUG)
SEED_INITIAL_PRODUCTS = env_bool("DJANGO_SEED_INITIAL_PRODUCTS", default=False)

# Secure defaults are enabled automatically outside local development.
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(os.getenv("DJANGO_SECURE_HSTS_SECONDS", "31536000"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
