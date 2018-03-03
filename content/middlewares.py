from django.conf import settings
from django.utils.http import urlquote
from django import http
from django.http import HttpResponse
import random

class NoCacheHeaderMiddleware(object):
    """
    Removing these headers and allowing apache to handle it.
    """
    def process_response(self, request, response):
        try:
            del response['Cache-Control']
            del response['Expires']
            del response['Last-Modified']
        except:
            pass
        return response


class RedirectTypoDomains(object):
    """
    Redirects typo domains to gafv homepage 75% of the time
    """
    def process_request(self, request):
        try:
            if not settings.TYPO_DOMAINS:
                # redirector not configured, don't do anything
                return None
        except AttributeError, e:
            return None
        host = request.get_host()
        #print host
        typos = settings.TYPO_DOMAINS
        #print typos
        for typo in typos:
            if host.endswith(typo):
                # Matched a typo, redirect 75% to gafv
                if random.randint(0,3) == 3:
                    return http.HttpResponseRedirect("http://www.youtube.com/")
                else:
                    return http.HttpResponseRedirect("http://www.getaudiofromvideo.com/")
        return None


class EnforceHostnameMiddleware(object):
    """
Enforce the hostname per the ENFORCE_HOSTNAME setting in the project's settings
The ENFORCE_HOSTNAME can either be a single host or a list of acceptable hosts
"""
    def process_request(self, request):
        """Enforce the host name"""
        try:
            if not settings.ENFORCE_HOSTNAME:
                # enforce not being used, don't do anything
                return None
        except AttributeError, e:
            return None
        
        host = request.get_host()
        if '/admin' in request.path or 'paypal_r' in request.path:
            return None
        # find the allowed host name(s)
        allowed_hosts = settings.ENFORCE_HOSTNAME
        if not isinstance(allowed_hosts, list):
            allowed_hosts = [allowed_hosts]
        if host in allowed_hosts:
            return None
        
        # redirect to the proper host name
        new_url = [allowed_hosts[0], request.path]
        new_url = "%s://%s%s" % (
            request.is_secure() and 'https' or 'http',
            new_url[0], urlquote(new_url[1]))
        if request.GET:
            new_url += '?' + request.META['QUERY_STRING']

        return http.HttpResponsePermanentRedirect(new_url)