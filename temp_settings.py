from .settings import *

# Remove the users app from INSTALLED_APPS temporarily
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'users']
