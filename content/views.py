from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from videos.models import Video
from django.db.models import Q
from django.core.cache import cache
import httplib2
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.views.decorators.cache import cache_page
from django.conf import settings

@cache_page(60 * 15)
def homepage(request):
#	context_instance=RequestContext(request)
	#print context_instance
#	for obj in context_instance:
#		if obj.has_key("userdetails"):
#			auth = obj["userdetails"]
	key = "homepagevids"
	v = cache.get(key)
	if v is None:
		v = Video.objects.all().filter(~Q(last_converted = None)).order_by("-last_converted")[:4]
		if len(v) < 4:
			v = Video.objects.all().order_by("-last_modified")
		v = v[:4]
		cache.set(key, v, 10 * 60)
	return render_to_response('homepage.html', {"recent": v, 'hide_back_button': True}, context_instance=RequestContext(request))

@csrf_exempt
def paypal_proxy(request):
	POST = request.read()
	print "paypal", POST
	if hasattr(settings, 'AMEMBER_URL'):
		destination = "https://%s/payment/paypal/ipn" % settings.AMEMBER_URL
	else:
		destination = "https://members.getaudiofromvideo.com/payment/paypal/ipn"
	h = httplib2.Http()
	headers = {
		"Content-Type": "application/x-www-form-urlencoded"
	}
	r, c = h.request(destination, "POST", POST, headers=headers)
	return HttpResponse(content=c, status=int(r["status"]))
