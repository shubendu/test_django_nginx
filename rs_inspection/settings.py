"""
Django settings for rs_inspection project.

Generated by 'django-admin startproject' using Django 3.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import os
import environ
import django_heroku

from django.contrib.messages import constants as messages
from pathlib import Path
from datetime import timedelta

# root = environ.Path(__file__) - 3  # get root of the project
env = environ.Env()
env.read_env()  # reading .env file


APP_ENV = env.str('APP_ENV', default='production')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
TEMPLATES_DIR = BASE_DIR / 'templates'
# BASE_DIR = root()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '3n(55d@wa!5!p0r-36ebdl-yvv+ma9#vqz%ig=owr%81onqzfy'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=False)

ALLOWED_HOSTS = [
    'ew4rb17abf.execute-api.eu-west-2.amazonaws.com',
    'rs-inspections.eba-ws4av6sy.eu-west-2.elasticbeanstalk.com',
    'rsinspections.eba-ws4av6sy.eu-west-2.elasticbeanstalk.com',
    'inspections.rs-recovery.com',
    'localhost',
    '18.234.9.101',
    '3.8.1.6'
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 3rd party apps
    'storages',
    'rest_framework',               # https://www.django-rest-framework.org/
    'drf_yasg',
    'compressor',
    'corsheaders',                  # https://github.com/zestedesavoir/django-cors-middleware
    'crispy_forms',
    'crispy_bootstrap5',
    'tinymce',
    # 'django_jinja',

    # custom apps
    'inspections',
    'pages',
    'users',
    'utils',
    'search',
    'config_app',
    'inspection_template',
    'vehicle',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # 'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # https://github.com/zestedesavoir/django-cors-middleware
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'rs_inspection.urls'

TEMPLATES = [
    # {
    #     'BACKEND': 'django_jinja.backend.Jinja2',
    #     'APP_DIRS': True,
    #     'OPTIONS': {
    #         "match_extension": ".jinja",
    #     },
    # },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR, ],
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

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

CRISPY_TEMPLATE_PACK = "bootstrap5"

WSGI_APPLICATION = 'rs_inspection.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
if (APP_ENV == 'dev' or APP_ENV == 'staging'):
    DATABASES = {
        'default': env.db('STAGING_DATABASE_URL', default='')
    }
else:
    DATABASES = {
        'default': env.db('DATABASE_URL', default='')
    }


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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

# if(APP_ENV=='dev'):
LOGIN_REDIRECT_URL = '/'
# else:
#     LOGIN_REDIRECT_URL = '/dev/'


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
]

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'), ]

# media files
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'


COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)

# if(APP_ENV=='dev'):
STATIC_URL = '/static/'  # '/static/'
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# else:
#     # Django’s STATIC_URL must end in a slash and the AWS_S3_CUSTOM_DOMAIN must not. It is best to set this variable independently of STATIC_URL.
#     # https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html #
#     # STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
#     AWS_ACCESS_KEY_ID = env.str('AWS_ACCESS_KEY_ID', default='') # django-site
#     AWS_SECRET_ACCESS_KEY = env.str('AWS_SECRET_ACCESS_KEY', default='')
#     AWS_STORAGE_BUCKET_NAME = env.str('AWS_STORAGE_BUCKET_NAME', default='static.rs-recovery.com')
#     # AWS_S3_ENDPOINT_URL = ''
#     AWS_S3_REGION_NAME = env.str('AWS_S3_REGION_NAME', default='eu-west-2') # London
#     # AWS_S3_CUSTOM_DOMAIN = ''
#     #######
#     AWS_S3_CUSTOM_DOMAIN = env.str('AWS_S3_CUSTOM_DOMAIN', default='s3.%s.amazonaws.com/%s' % (AWS_S3_REGION_NAME, AWS_STORAGE_BUCKET_NAME))
#     AWS_S3_OBJECT_PARAMETERS = {
#         'CacheControl': 'max-age=86400',
#     }
#     AWS_LOCATION = env.str('AWS_LOCATION', default='static')

#     STATIC_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
#     STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
#     COMPRESS_STORAGE = STATICFILES_STORAGE

COMPRESS_URL = STATIC_URL


# https://www.django-rest-framework.org/
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        # 'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
        'rest_framework.permissions.DjangoModelPermissions'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # 'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
}

# https://django-rest-framework-simplejwt.readthedocs.io/en/latest/settings.html
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(weeks=1),
    'ROTATE_REFRESH_TOKENS': True,
    # 'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    # 'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    # 'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(weeks=1),
    'AUTH_TOKEN_CLASSES': (
        'rest_framework_simplejwt.tokens.AccessToken',  # Default
        # 'rest_framework_simplejwt.tokens.SlidingToken',
    ),
    # 'SIGNING_KEY': SECRET_KEY,
}


# https://github.com/zestedesavoir/django-cors-middleware
CORS_ORIGIN_ALLOW_ALL = True
# CORS_ORIGIN_WHITELIST = (
#     'rs-recovery.com',
#     'localhost:3000'
# )

if (APP_ENV == 'dev'):
    SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'] = timedelta(minutes=50)
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = env.str('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD')
    EMAIL_FILE_PATH = str(BASE_DIR.joinpath('sent_emails'))
    AUTH_PASSWORD_VALIDATORS = []
else:
    # https://github.com/django-ses/django-ses
    DEFAULT_FROM_EMAIL = 'RSR Inspections Portal <noreply@rs-recovery.com>'
    EMAIL_BACKEND = 'django_ses.SESBackend'
    AWS_SES_ACCESS_KEY_ID = env.str('AWS_SES_ACCESS_KEY_ID', default='')
    AWS_SES_SECRET_ACCESS_KEY = env.str(
        'AWS_SES_SECRET_ACCESS_KEY', default='')
    AWS_SES_REGION_NAME = 'eu-west-2'  # London
    AWS_SES_REGION_ENDPOINT = 'email.eu-west-2.amazonaws.com'


# Activate Django-Heroku.
# https://github.com/heroku/django-heroku
# django_heroku.settings(locals(), staticfiles=False)
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

TINYMCE_DEFAULT_CONFIG = {

    'height': 360,
    'width': 750,
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 20,
    'selector': 'textarea',
    'theme': 'modern',
    'plugins': '''
   textcolor save link image media preview codesample contextmenu
   table code lists fullscreen insertdatetime nonbreaking
   contextmenu directionality searchreplace wordcount visualblocks
   visualchars code fullscreen autolink lists charmap print hr
   anchor pagebreak
   ''',
    'toolbar1': '''
   fullscreen preview bold italic underline | fontselect,
   fontsizeselect | forecolor backcolor | alignleft alignright |
   aligncenter alignjustify | indent outdent | bullist numlist table |
   | link image media | codesample |
   ''',
    'toolbar2': '''
   visualblocks visualchars |
   charmap hr pagebreak nonbreaking anchor | code |
   ''',
    'contextmenu': 'formats | link image',
    'menubar': True,
    'statusbar': True,
}

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}
