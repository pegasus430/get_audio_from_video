import os, sys
import newrelic.agent

newrelic.agent.initialize('/var/www/gafv/newrelic.ini')

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ['DJANGO_SETTINGS_MODULE'] = 'gafv.settings'

os.environ["CELERY_LOADER"] = "django"

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
application = newrelic.agent.wsgi_application()(application)

