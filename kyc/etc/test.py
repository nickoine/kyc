from .base import *
import os

# Test Environment Settings
DEBUG = False  # Tests should run with DEBUG off for realism
ALLOWED_HOSTS = ['*']  # Allow all hosts during testing

# Database Configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('TEST_DB_NAME', default='test_db'),
        'USER': os.getenv('TEST_DB_USER', default='test_dev'),
        'PASSWORD': os.getenv('TEST_DB_PASSWORD', default='password'),
        'HOST': os.getenv('DB_HOST', default='localhost'),
        'PORT': os.getenv('TEST_DB_PORT', default=5434),
    }
}

# Static files (For running tests with static content if needed)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Docker Environment Check
if os.getenv('DOCKERIZED', 'false').lower() == 'true':
    DATABASES['default']['HOST'] = 'db'  # Use Docker container name for PostgreSQL host

# Jenkins Test Configuration
if os.getenv('JENKINS', 'false').lower() == 'true':
    pass

# Test Runner Configuration
TEST_RUNNER = 'django.test.runner.DiscoverRunner'
