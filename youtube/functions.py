import gdata.youtube
import gdata.youtube.service
from videos.models import Video
from videos.slugify import unique_slugify
import re,datetime,base64
from django.core.cache import cache
import threading

yt_service = gdata.youtube.service.YouTubeService()


"""
Prefably access to methods in this file should be made using a task que
"""

def get_date(timestamp):
    """
    Takes iso8601 formated timestamp string and parses it into datetime object
    """
    return datetime.datetime(*map(int, re.split('[^\d]', timestamp)[:-1]))


def getid(entry):
    ytid = entry.id.text.replace("http://gdata.youtube.com/feeds/videos/", "")
    ytid = ytid.replace("http://gdata.youtube.com/feeds/api/videos/", "")
    return ytid


def save_obj_from_entry(entry):
    """
    Takes entry(gdata) object and stores it into db
    """
    v = Video()
    v.title = entry.media.title.text
    v.ytid = getid(entry)
    unique_slugify(v, v.title)
    v.duration = int(entry.media.duration.seconds)
    v.description = entry.media.description.text
    v.published_on = get_date(entry.published.text)
    v.category = entry.media.category[0].text
    if entry.rating is not None:
        v.rating = float(entry.rating.average)
    if entry.media.thumbnail is not None:
        v.thumbnail = entry.media.thumbnail[0].url
    try:
        v.views = int(entry.statistics.view_count)
    except:
        v.views = 0
    v.save()
    return v


class VideoGetter(threading.Thread):
    def __init__(self, ytid):
        self.ytid = ytid
        threading.Thread.__init__(self)


    def run(self):
        try:
            self.result = get_save_video_details(self.ytid)
        except:
            self.result = None
    
    def get_result(self):
        return self.result


def get_related_details(videolist):
    output = []
    threads = []
    for vid in videolist:
        t = VideoGetter(vid)
        t.start()
        threads += [t]
    #print threads
    for t in threads:
        t.join()
        result = t.get_result()
        if result is not None:
            output += [result]
        #output += [get_save_video_details(vid)]
    return output


def get_related_videos(video):
    key = base64.b64encode("get_related-%s" %(video.ytid))
    related = cache.get(key)
    if related is None:
        related = []
        if video.related:
            ids = video.related.split(",")
#            for r in video.related.split(","):
#                related += [get_save_video_details(r)]
        else:
            r = yt_service.GetYouTubeRelatedVideoFeed(video_id=video.ytid)
            ids = []
            for entry in r.entry[:4]:
                try:
                    id = getid(entry)
                    ids += [id]
                    #related += [get_save_video_details(id)]
                except:
                    pass
            video.related = (",").join(ids)
            video.save()
        related = get_related_details(ids)
        cache.set(key, related, 10 * 24 * 60 * 60)
    return related

def get_save_video_details(ytid, entry=None):
    """
    Returns Video object for given ytid. Creates it if needed.
    """
    try:
        v = Video.objects.get(ytid=ytid)
    except Video.DoesNotExist:
        if entry is None:
            #print "fetching yt"
            entry = yt_service.GetYouTubeVideoEntry(video_id=ytid)
        v = save_obj_from_entry(entry)
    return v


def search_for_videos(search_terms, page=1, catsearch=False):
    try:
        key = base64.b64encode("ytsearch-%s-%s-%s" %(search_terms, page, catsearch))
    except:
        # got unicode errors occasionally
        search_terms = search_terms.encode("utf8")
        key = base64.b64encode("ytsearch-%s-%s-%s" %(search_terms, page, catsearch))
    #print key
    output = cache.get(key)
    if output is None:
        output = {}
        query = gdata.youtube.service.YouTubeVideoQuery()
        if catsearch:
            query.categories.append('/%s' % search_terms.title())
        else:
            query.vq = search_terms
        query.start_index = ((page - 1) * 12) + 1
        feed = yt_service.YouTubeQuery(query)
        results = []
        for entry in feed.entry[:12]:
            results += [get_save_video_details(getid(entry), entry=entry)]
        total = feed.total_results.text
        total = int(total)
        if total > 1000:
            """
            Cause youtube API does not allow requesting beyond item 1000
            RequestError: {'status': 400, 'body': 'You cannot request beyond item 1000.', 'reason': 'Bad Request'}
            """
            total = 1000
        output["results"] = results
        output["total"] = total
        cache.set(key, output, 1 * 60 * 60)
    else:
        total = output["total"]
        results = output["results"]

    return results, total

def get_video_from_track_info(info):
    search_terms = "%s %s" % (info.get("name"), info.get("artists")[0].get("name"))
    results, total = search_for_videos(search_terms)
    if len(results) == 0:
        return None
    total = int(total)
    durations = []
    for result in results:
        durations.append(abs(result.duration-info.get("length")))
        
    delta = 0
    if delta in durations:
        return results[durations.index(delta)]

    delta = durations[0]
    for d in durations:
        if delta > d:
            delta = d
    return results[durations.index(delta)]


def get_video_from_track_info2(name, artist, length):
    search_terms = "%s %s" % (name, artist)
    results, total = search_for_videos(search_terms)
    if len(results) == 0:
        return None

    durations = []
    for result in results:
        durations.append(abs(result.duration-length))

    
    delta = 0
    if delta in durations:
        return results[durations.index(delta)]

    delta = durations[0]
    for d in durations:
        if delta > d:
            delta = d
    return results[durations.index(delta)]

def get_video_from_track_info3(ytid):
    video = get_save_video_details(ytid)
    return video
