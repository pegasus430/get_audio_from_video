from videos.models import Video
from youtube.functions import get_save_video_details, search_for_videos, get_related_videos
from youtube.functions import get_video_from_track_info
from youtube.api_v3 import search_for_videos as search_for_videos_v3
from youtube.api_v3 import get_save_video_details as get_save_video_details_v3
from django.shortcuts import redirect, get_object_or_404, render_to_response
from django.http import HttpResponse, Http404, HttpResponsePermanentRedirect
import urlparse, base64
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.conf import settings


def converter_page(request, slug):
    query = request.session.get('searchterm', "")
    try:
        v = Video.objects.get(slug=slug)
    except Video.DoesNotExist:
        raise Http404
    related = None
    return render_to_response('convert.html', {
        "video": v, 
        "related": related, 
        "query": query,
        "GOOGLE_API_KEY": settings.GOOGLE_API_KEY
        },
        context_instance=RequestContext(request)
    )


def grab_and_redirect(request, ytid):
    ytid = ytid.split("/")[0]
    key = base64.b64encode("grabredir-%s" %(ytid))
    dest = cache.get(key)
    if dest is None:
        dest = "NA"
        try:
            v = get_save_video_details_v3(ytid)
            dest = request.build_absolute_uri(v.get_absolute_url())
#            return redirect(v, permanent=True)
        except:
            dest = "NA"
#            return HttpResponse("Not Found", status=404)
        cache.set(key, dest, 10 * 24 * 60 * 60) #cache for 10 days, dont care!
    if dest == "NA":
        return HttpResponse("Not Found", status=404)
    else:
        return HttpResponsePermanentRedirect(dest)


def guessvideo(url):
    try:
        u = urlparse.urlparse(url)
        if u.hostname == 'youtu.be':
            ytid = u.path[1:]
            v = get_save_video_details_v3(ytid)
            return v
        elif "spotify.com" in u.hostname:
            from spotify import Spotify
            info = Spotify.get_track_info(url)
            video = get_video_from_track_info(info.get("track"))
            return video
        elif u.hostname is not None and u.hostname != '':
            ytid = urlparse.parse_qs(u.query)['v'][0]
            v = get_save_video_details_v3(ytid)
            return v
        else:
            return None
    except:
        return None


def catpage(request, catname, page=1):
    videos, total = search_for_videos(catname, catsearch=True)
    return render_to_response('category.html', {"videos": videos}, context_instance=RequestContext(request))

@csrf_exempt
def basicsearch(request):
    if request.method == 'GET':
        query = request.session.get('searchterm', "")
        page = request.session.get('page', 1)
        if query == "":
            return render_to_response('search.html', {}, context_instance=RequestContext(request))
        else:
            return do_search(request, query, page)
    else:
        query = request.POST.get("query", None)
        #print query
        if query is None or query == '':
            return HttpResponse("need to enter query")
        else:
            v = guessvideo(query)
            if v is not None:
                """
                Entered query is a url
                """
                return redirect(v)
            else:
                page = request.POST.get("page", 1)
                try:
                    page = int(page)
                except:
                    page = 1
                return do_search(request, query, page)              

def do_search(request, query, page):
    request.session['searchterm'] = query
    request.session['page'] = page
    results, total = search_for_videos_v3(query, page=page)
    total = int(total)
    last_page = ((total -1) / 12) + 1
    if last_page > 82:
        last_page = 82
    if page == 1:
        pre = 1
    else:
        pre = page - 1
    if page == last_page:
        next = last_page
    else:
        next = page + 1
    pages = range(1, page)[-3:] + [page] + range(page, last_page)[:3]
    pages = list(set(pages))
    pages.sort()
    return render_to_response('search.html', {"pre": pre, "next":next, "last_page": last_page, "videos": results, "total": total, "page": page, "query": query, "pages": pages}, context_instance=RequestContext(request))
