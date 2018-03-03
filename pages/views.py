# Create your views here.
from django.template import RequestContext
from django.shortcuts import redirect, get_object_or_404, render_to_response
from pages.models import Page
from django.views.decorators.cache import cache_page


@cache_page(60 * 15)
def show_page(request, slug):
	p = get_object_or_404(Page, slug=slug)
	return render_to_response('page.html', {"page": p}, context_instance=RequestContext(request))