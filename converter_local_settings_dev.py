def fetch_webserver_ip():
    """
    Fetches public ip of gafv webserver, then looks up ec2 api for its internal ip
    """
    import socket
    #Get ip of gafv
    gafv = socket.gethostbyname("devamember.getaudiofromvideo.com")
    #print gafv
    #Get hostname of that ip
    hostname = socket.gethostbyaddr(gafv)[0]
    #print hostname
    #get ip of that hostname
    return socket.gethostbyname(hostname)

BROKER_HOST = fetch_webserver_ip()
CELERY_RESULT_BACKEND = "amqp"
CELERYD_PREFETCH_MULTIPLIER = 1
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'data.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}
DEBUG = False

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}
MEDIA_URL = 'http://127.0.0.1:8000/static/'
