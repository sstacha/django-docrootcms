# ------------------------ DOCROOT CMS SETTINGS ------------------------------------
# add our different roots for static files to be served up
import os

try:
    STATIC_ROOT
except NameError:
    STATIC_ROOT = os.path.join(BASE_DIR, "static/")
# IMAGES_ROOT = os.path.join(BASE_DIR, "images/")
# CACHED_ROOT = os.path.join(BASE_DIR, "cache/")
DOCROOT_ROOT = os.path.join(BASE_DIR, "docroot/files/")
# STATICFILES_DIRS = (
#     IMAGES_ROOT,
#     CACHED_ROOT,
#     DOCROOT_ROOT,
# )

# add our docroot application to the installed apps and middleware initializations
# NOTE: I am always seeing INSTALLED_APPS & MIDDLEWARE as a modifiable list; if changed to tuple this will fail!
if 'docroot' not in INSTALLED_APPS and 'docrootcms' in INSTALLED_APPS:
    # insert docroot at the beginning so we can override admin/login templates in docroot; revert to below if not
    INSTALLED_APPS.insert(0, 'docroot')
    # docrootcms_idx = INSTALLED_APPS.index('docrootcms')
    # INSTALLED_APPS.insert(docrootcms_idx, 'docroot')

if 'docroot' in INSTALLED_APPS:
    MIDDLEWARE += ('docrootcms.middleware.DocrootFallbackMiddleware',)
# else:
#     print("WARNING: 'docroot' was not found in INSTALLED_APPS so we are skipping setting up the middleware!")

# added for a problem in the way apache handles WSGI; would like to push this to web server at some point
#   to eliminate 2 file checks for every request
# don't allow our cms to serve up any templates or python code as static files; include .htaccess for good measure
# to disable checks set USE_STATIC_FORBIDDEN = False (eliminates 2 file system checks per request)
USE_STATIC_FORBIDDEN = False
STATIC_FORBIDDEN_EXTENSIONS = ['.dt', '.py', ]
STATIC_FORBIDDEN_FILE_NAMES = ['.htaccess', ]
# We tell django to not append slashes as this messes with our combined static/dynamic template pages docroot
# APPEND_SLASH = False
# Adding variable to tell our stuff to not be language aware for the default language (no /en/ appended)
#   This is helpful for troubleshooting migrated DjangoCMS pages
IGNORE_LANGUAGE_PREFIX = True
# DISABLE_AUTHENTICATION = True

# add logging and our loggers
LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        # 'file': {
        #     'level': 'DEBUG',
        #     'class': 'logging.FileHandler',
        #     'filename': './django.log',
        #     'formatter': 'simple'
        # },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'docroot': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}
if DEBUG:
    # make all loggers use the console.
    for logger in LOGGING['loggers']:
        LOGGING['loggers'][logger]['handlers'] = ['console']
else:
    # make sure all production servers never show debugging info.  set them to info if they are debug
    for logger in LOGGING['loggers']:
        if LOGGING['loggers'][logger]['level'] == 'DEBUG':
            LOGGING['loggers'][logger]['level'] = 'INFO'

# OVERRIDING DATABASE LOCATION AND NAME FOR EASY SHARING
# NOTE: we are only overriding for sqllite3.  Move the db block below this if you don't want any overrides.
if 'default' in DATABASES and 'ENGINE' in DATABASES['default'] and DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
    DATABASES['default']['NAME']=os.path.join(BASE_DIR, 'data', 'db.sqlite3')

# OVERRIDE THE DEFAULT CACHE TO DISABLE TEMPLATE CACHING IN DEV
if DEBUG:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        },
    }

# SECURITY WARNING: keep the secret key used in production a secret!
# NOTE: Recommend using a DOCROOTCMS_SECRET_KEY environment variable which will get replaced at runtime below
# Replace any DOCROOTCMS_ prefixed environment variables in settings at startup
# NOTE: used for docker/local machine environment variable loading overrides
import sys
this_module = sys.modules[__name__]
for k, v in os.environ.items():
    if k.startswith("DOCROOTCMS_"):
        attr_key = k[5:]
        if attr_key:
            # print (f"attempting to set {attr_key} to [{str(v)}]")
            setattr(this_module, attr_key, v)

# ------------------------ DOCROOT CMS SETTINGS ------------------------------------
