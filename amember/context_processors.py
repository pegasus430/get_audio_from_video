from amember.views import getauth
from django.conf import settings


def testing(request):
	return {"userdetails":None}
    #return {"userdetails":getauth(request)}


def amember_url(request):
	if hasattr(settings, 'AMEMBER_URL'):
		return {"amember_url": settings.AMEMBER_URL}
	return {"amember_url": "members.getaudiofromvideo.com"}

