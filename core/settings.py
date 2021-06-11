import os
import environ
env = environ.Env()
environ.Env.read_env()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = '9yh&mdgvf_d&k=4wisdom9=+a)ali!9smfg&b4_+x3u&#Sol#vd'


# SECURITY WARNING: don't run with debug turned on in production!
APP_NAME = "Access Retail"
DEBUG = env('DEBUG')

# DEVELOPMENT = "PRODUCTION"
# DEVELOPMENT = "STAGING"
DEVELOPMENT = "LOCAL"

INTERNAL_IPS = [
    '0.0.0.0',
    '127.0.0.1',
]
ALLOWED_HOSTS = ['*']



# Application definition
INSTALLED_APPS = [
    #Django Core apps
    'admin_interface', #Installed Apps
    'colorfield', #Installed Apps

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #Installed Apps

    #For Development
    'data_browser',
    "var_dump",
    'debug_toolbar',
    'debugtools',
    #For Production
    'ajax_datatable',
    'django_filters',
    'django_tables2',
    'jsonify',
    'django_json_widget',
    'django_jsonfield_backport',
    'rest_framework',
    'corsheaders',
    'crispy_forms',
    'mptt',
    'django_mptt_admin',
    'easyaudit',
    'django_extensions',

    'simple_import',
    'import_export',
    'report_builder',

    #Projects Apps
    # 'custom_field.apps.CustomFieldConfig',
    'master_setups.apps.MasterSetupsConfig',
]




MIDDLEWARE = [

    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', # Note that this needs to be placed above CommonMiddleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #Installed Apps

    'easyaudit.middleware.easyaudit.EasyAuditMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    #Projects Apps

]

REST_FRAMEWORK = {
   'DEFAULT_AUTHENTICATION_CLASSES': (
       'rest_framework.authentication.TokenAuthentication',
   ),
   'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAdminUser'
   ),
}

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_PERMISSION_CLASSES': (
        # 'rest_framework.permissions.IsAuthenticated',
        'rest_framework.permissions.IsAdminUser',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        # 'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
}

CORS_ORIGIN_WHITELIST = [
    'http://localhost:3000',
    'http://localhost:8000',
]

ROOT_URLCONF = 'core.urls'
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")  # ROOT dir for templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                #Installed Apps
                'django.template.context_processors.static',
                'django.template.context_processors.media',
                'core.context.global_context'
            ],
           'builtins': [                                     # Add this section
                "debugtools.templatetags.debugtools_tags",   # Add this line
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

if DEVELOPMENT=="PRODUCTION":
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env("DB_NAME"),
            'USER': env("DB_USER"),
            'PASSWORD': env("DB_PASSWORD"),
            'HOST': env("DB_HOST"),
            'PORT': env("DB_PORT"),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
    # DATABASES = {
    #     'default': {
    #         'ENGINE': 'django.db.backends.postgresql',
    #         'NAME': env("DB_NAME"),
    #         'USER': env("DB_USER"),
    #         'PASSWORD': env("DB_PASSWORD"),
    #         'HOST': env("DB_HOST"),
    #         'PORT': env("DB_PORT"),
    #     }
    # }





# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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


# CACHES = {
#     "select2": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": "redis://127.0.0.1:6379/2",
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#         }
#     }
# }

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR,"static")
]
MEDIA_URL = '/media/'
MEDIA_ROOT=os.path.join(BASE_DIR,"media")

STATIC_ROOT = "static_root"
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

AUTH_USER_MODEL = 'master_setups.User'
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
LOGIN_REDIRECT_URL = "/home"
LOGIN_URL = "/login"
LOGOUT_REDIRECT_URL = "/"
CRISPY_TEMPLATE_PACK = 'bootstrap4'
DJANGO_TABLES2_TEMPLATE = "django_tables2/bootstrap4.html"

MPTT_DEFAULT_LEVEL_INDICATOR = "+--"
DEFAULT_LEVEL_INDICATOR = "+--"
#exclude eady audit models
DJANGO_EASY_AUDIT_UNREGISTERED_CLASSES_EXTRA = [

                        ]

# AJAX_DATATABLE_MAX_COLUMNS = 100
# AJAX_DATATABLE_TRACE_COLUMNDEFS = True
# AJAX_DATATABLE_TRACE_QUERYDICT = True
# AJAX_DATATABLE_TRACE_QUERYSET = True
# AJAX_DATATABLE_TEST_FILTERS = True
# AJAX_DATATABLE_DISABLE_QUERYSET_OPTIMIZATION = True


if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    X_FRAME_OPTIONS = "DENY"

    ALLOWED_HOSTS = ["*"]

    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = ''
    EMAIL_HOST_USER = ''
    EMAIL_HOST_PASSWORD = ''
    EMAIL_USE_TLS = True
    EMAIL_PORT = ''
    DEFAULT_FROM_EMAIL = ''


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': True,
        },
        'werkzeug': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
    # 'loggers': {
    #     'django.db.backends': {
    #         'handlers': ['console'],
    #         'level': 'DEBUG',
    #     },
    # },
}