from config.settings.base import *
import dj_database_url

DEBUG = True

SHOPIFY_APP_API_KEY = os.environ.get('SHOPIFY_APP_API_KEY')
SHOPIFY_APP_API_SECRET = os.environ.get('SHOPIFY_APP_API_SECRET')
SHOPIFY_APP_IS_EMBEDDED = True
SHOPIFY_APP_DEV_MODE = False

DATABASE_URL = os.environ.get("DATABASE_URL", os.environ.get('DATABASE_URL'))

DATABASES = {
    'default': dj_database_url.config(default=DATABASE_URL)
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.path.join(ROOT_DIR, 'staticfiles')

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(ROOT_DIR, 'static'),
)

CRM_HOST = os.environ.get('CRM_HOST')
