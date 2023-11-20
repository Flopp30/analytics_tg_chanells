import os
from pathlib import Path
from environs import Env
import dj_database_url

env = Env()
env.read_env()

# Telegram Definition
TG_API_ID = env('TG_API_ID', None)
TG_API_HASH = env('TG_API_HASH', None)
TG_PHONE_NUMBER = env('TG_PHONE_NUMBER', None)

# Django definition
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = env('DJ_SECRET_KEY', 'django-insecure-6)t2by)g89_nb^)5fxef$vfwh!#@rr#u+zn=y3_=vwo#x!1k^&')
DEBUG = env.bool('DJ_DEBUG', True)
ALLOWED_HOSTS = env.list('DJ_ALLOWED_HOSTS', ['*'])
CSRF_TRUSTED_ORIGINS = env.list('DJ_CSRF_TRUSTED_ORIGINS', [])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # custom
    "bot_parts",
    "channel",
    "message",
    "metrics",
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

ROOT_URLCONF = 'analitics_tg_channels.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
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

WSGI_APPLICATION = 'analitics_tg_channels.wsgi.application'

DATABASES = {
    'default': dj_database_url.parse(
        env('DJ_DB_URL', 'sqlite:///db.sqlite3'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

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

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{asctime} {levelname} {name} | {filename}>{funcName}():{lineno} | {message}',
            'style': '{',
        },
        'simple': {
            'format': '{asctime} {levelname} {module} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        # 'mail_admins': {
        #     'level': 'ERROR',
        #     'class': 'django.utils.log.AdminEmailHandler',
        #     'include_html': True,
        #     'filters': ['require_debug_false']
        # },
        'debug_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': env('DEBUG_LOG', './logs/django-debug.log'),
            'filters': ['require_debug_true']
        },
        'errors_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': env('ERROR_LOG', './logs/django-error.log'),
            'when': 'MIDNIGHT',
            'backupCount': 7,
            'formatter': 'verbose',
        },
        'base_log': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': env('BASE_LOG', './logs/django-base.log'),
            'when': 'MIDNIGHT',
            'backupCount': 7,
            'formatter': 'verbose',
        },
        'base_log_warning': {
            'level': 'WARNING',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': env('BASE_LOG', './logs/django-base.log'),
            'when': 'MIDNIGHT',
            'backupCount': 7,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.security.DisallowedHost': {
            'handlers': ['console', 'errors_file', 'base_log'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django': {
            'handlers': ['console', 'errors_file', 'base_log'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.db': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': True,
        },
        'django.server': {
            'level': 'INFO',
            'handlers': ['console', 'base_log_warning'],
            'propagate': False,
        },
        '': {
            'level': 'INFO',
            'handlers': ['console', 'base_log', 'errors_file'],
            'propagate': True,
        }
    }
}

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'

STATIC_ROOT = './static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
