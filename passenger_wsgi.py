# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, '/var/www/u0865207/data/www/journal.amumgk.ru/journal')
sys.path.insert(1, '/var/www/u0865207/data/djangoenv/lib/python3.7/site-packages')
os.environ['DJANGO_SETTINGS_MODULE'] = 'journal.settings'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
