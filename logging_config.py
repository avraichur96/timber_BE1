# Configure logging to see errors in server logs

# 1. Add this to your Django settings.py:

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.organizations': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# 2. Add the custom exception handler to your REST_FRAMEWORK settings:

REST_FRAMEWORK = {
    # ... your existing settings ...
    'EXCEPTION_HANDLER': 'apps.organizations.exceptions.custom_exception_handler',
    # ... other settings ...
}

# 3. To see logs in development, run with:
# python manage.py runserver --settings=yourproject.settings

# 4. To see logs in production, check the django.log file or use:
# tail -f django.log

# 5. For more detailed logging, you can also set:
# DEBUG = False (in production)
# This will ensure proper 500 responses instead of debug pages
