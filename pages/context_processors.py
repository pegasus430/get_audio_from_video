from pages.models import Page
from django.core.cache import cache

def build_menu(request):
	key = "footerlinks"
	output = cache.get(key)
	if output is None:
		pages = Page.objects.all().filter(weight__gte=1)
		count = len(pages)
		mid = count/2
		midf = count/2.0
		if mid != midf:
			mid += 1
		output = [pages[:mid], pages[mid:]]
		cache.set(key, output, 14 * 60)
	return {"menu": output}