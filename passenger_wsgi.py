# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, '/var/www/u2534371/data/www/reklamaoko.ru/oko_project')
#sys.path.insert(1, '/var/www/u2534371/data/djangoenv/lib/python3.8.6/site-packages')
# sys.path.insert(1, '/var/www/u2534371/data/djangoenv/lib/python3.7/site-packages')
sys.path.insert(1, '/var/www/u2534371/data/djangoenv/lib/python3.9/site-packages')
os.environ['DJANGO_SETTINGS_MODULE'] = 'oko_project.settings'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()