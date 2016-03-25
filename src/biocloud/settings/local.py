from .base import *             # NOQA
import sys
import logging.config

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Turn off debug while imported by Celery with a workaround
# See http://stackoverflow.com/a/4806384
# if 'celery' in sys.argv[0]:
#     DEBUG = False

# Django Debug Toolbar
INSTALLED_APPS += ('debug_toolbar.apps.DebugToolbarConfig',)

# Show emails to console in DEBUG mode
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Log everything to the logs directory at the top
LOGFILE_ROOT = join(dirname(BASE_DIR), 'logs')

# Reset logging
# http://www.caktusgroup.com/blog/2015/01/27/
# Django-Logging-Configuration-logging_config-default-settings-logger/

LOGGING_CONFIG = None
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': (
                '[%(asctime)s] %(levelname)s '
                '[%(pathname)s:%(lineno)s] %(message)s'
            ),
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'django_log_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': join(LOGFILE_ROOT, 'django.log'),
            'formatter': 'verbose'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['django_log_file', ],
            'propagate': True,
            'level': 'DEBUG',
        },
    }
}

for app in LOCAL_APPS:
    app_handler = '%s_log_file' % app
    app_log_filepath = '%s.log' % app
    LOGGING['loggers'][app] = {
        'handlers': [app_handler, 'console', ],
        'level': 'DEBUG',
    }
    LOGGING['handlers'][app_handler] = {
        'level': 'DEBUG',
        'class': 'logging.FileHandler',
        'filename': join(LOGFILE_ROOT, app_log_filepath),
        'formatter': 'verbose',
    }

logging.config.dictConfig(LOGGING)

