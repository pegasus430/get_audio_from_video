# Create your views here.
from django.http import HttpResponse
from django.conf import settings
import urllib2, json


def showauth(request):
	return HttpResponse(str(getauth(request)))

def getauth(request):
	auth = {
		"user": None,
		"loggedin": False,
		"allowd_to_convert": False
	}
	try:
		sessid = request.COOKIES["PHPSESSID"]
	except:
		return auth

	if hasattr(settings, 'AMEMBER_URL'):
		url = "https://%s/get_session.php?sessid=sess_%s" % (settings.AMEMBER_URL, sessid)
	else:
		url = "https://members.getaudiofromvideo.com/get_session.php?sessid=sess_%s" %(sessid)

	j = urllib2.urlopen(url).read()
	sess = json.loads(j)
	"""
	Additional checks :-
		1) Session IP must match users IP
	"""
	try:
		auth["user"] = sess["_amember_user"]["login"]
		auth["loggedin"] = True
		try:
			subs = sess["_amember_subscriptions"]
			if len(subs) > 0:
				auth["allowd_to_convert"] = True
			else:
				auth["allowd_to_convert"] = False
		except:
			auth["allowd_to_convert"] = False
	except:
		auth["user"] = None
		auth["loggedin"] = False
	return auth