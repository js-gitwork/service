import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'din-secret-key'  # Erstat med din faktiske SECRET_KEY (hold den hemmelig!)

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'assets.apps.AssetsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # Sprogskift (skal være sidst)
]

ROOT_URLCONF = 'vprepair.urls'

# --- Templates ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # Fælles templates (f.eks. base.html)
        'APP_DIRS': True,  # Tillader Django at lede i app/templates/
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',  # Tilføjet for sprogstøtte
            ],
        },
    },
]

# --- Database ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # Moderne Path-sti
    }
}

# --- Sprog og internationalisering (i18n) ---
LANGUAGE_CODE = 'da'
USE_I18N = True  # Aktiver oversættelser
USE_L10N = True  # Aktiver lokalisering (f.eks. datoformater)
USE_TZ = True    # Aktiver tidszone-støtte

# Tilgængelige sprog (tilføj/rediger efter behov)
LANGUAGES = [
    ('da', 'Dansk'),
    ('en', 'English'),
    ('de', 'Deutsch'),
    ('pl', 'Polski'),
]

# Sti til oversættelsesfiler (opret mappen "locale" i projektroden)
LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

# --- Statiske filer (CSS, JS, billeder) ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]  # Ekstra sti til globale statiske filer
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')     # Samlet sti til production (kør `collectstatic`)

# --- Mediefiler (uploadede filer) ---
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# --- Login-URL (hvis du bruger django.contrib.auth) ---
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
