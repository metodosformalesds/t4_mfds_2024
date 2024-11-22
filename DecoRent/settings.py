"""
Django settings for DecoRent project.

Generated by 'django-admin startproject' using Django 4.2.16.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
import environ
from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-uz7))qty0ah^7744lcdxg7)0b=9rwo&kvq3g^k#65*55_f-g(5'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'https://mfdsteam4.pythonanywhere.com/', '4d4b-189-248-73-167.ngrok-free.app', 'deco-rent.com', 'www.deco-rent.com'] 
CSRF_TRUSTED_ORIGINS = ['https://4d4b-189-248-73-167.ngrok-free.app', 'https://deco-rent.com/']

# URL pública para producción
NGROK_URL = None  # Aqui se configuro la url de NGROK para hacer pruebas locales
PRODUCTION_URL = 'https://deco-rent.com'  # Se establece el dominio real

# Configuración de sesión
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Sesiones en la base de datos
SESSION_COOKIE_NAME = 'sessionid'  # Nombre de la cookie
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # La sesión no expira al cerrar el navegador
SESSION_COOKIE_HTTPONLY = True  # Asegura que las cookies no sean accesibles desde JavaScript


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',#Google
    'allauth',#Google
    'allauth.account',#Google
    'allauth.socialaccount',#Google
    'allauth.socialaccount.providers.google',#Google
    'Usuarios',
    'Servicios',
    'Solicitudes',
    'Pagos',
    'Notificaciones',
    'Calificaciones',
    'corsheaders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'corsheaders.middleware.CorsMiddleware',

]

CORS_ALLOW_ALL_ORIGINS = True



ROOT_URLCONF = 'DecoRent.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], 
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

WSGI_APPLICATION = 'DecoRent.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'decorent_db',
        'USER': 'root',
        'PASSWORD': 'metodosformales',
        'HOST': 'ls-e6ed3ee4a78219076dbfd973c1a20316966b96b6.c54wosoyoygd.us-west-2.rds.amazonaws.com',
        'PORT': '3306',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / "static",  # Agrega la carpeta estática global del proyecto
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#Directorio de archivos media (imagenes)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

AUTHENTICATION_BACKENDS = [
    'Usuarios.backends.EmailBackend',  # Backend de autenticacion personalizado
    'django.contrib.auth.backends.ModelBackend',  # Se mantiene el backend predeterminado para seguridad
    
    'allauth.account.auth_backends.AuthenticationBackend',#Google
]

# Define el campo email como el identificador para la autenticación
AUTH_USER_MODEL = 'Usuarios.User'  # Asegúrate de que apunte a tu modelo personalizado

#En caso de cambiar el ID para pruebas locales, volverlo a cambiar antes de hacer push al repositorio
SITE_ID = 4 #Se movio el ID

#API aws reko
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION_NAME = os.getenv('AWS_REGION_NAME', 'us-west-2')

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH2_CLIENT_ID': '612675233053-0m1q85c3u0jbvv5iu1cfnevp4sa7k76q.apps.googleusercontent.com',
        'OAUTH2_CLIENT_SECRET': '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',
    }
}
ACCOUNT_USER_MODEL_USERNAME_FIELD = None  # Indica que no se usa el campo username
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = 'optional'  # O puede ser 'mandatory', dependiendo de lo que prefieras
ACCOUNT_UNIQUE_EMAIL = True

LOGIN_REDIRECT_URL = 'servicios_sin_login'  # Redirige a la página principal (solucion temporal)

#Stripe
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')

#Inhabilita la plantilla HTML y pasa directamente a la seleccion de cuentas de Google
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_LOGIN_ON_GET = True
