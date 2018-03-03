from django.conf import settings
from django.core.cache import cache
from videos.models import Video
from videos.slugify import unique_slugify
from apiclient.discovery import build
import base64
import dateutil
import isodate


YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

youtube_api = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=settings.GOOGLE_API_KEY)


def save_obj_from_entry(response):
    """
    Takes response object and stores it into db
    """
    v = Video()
    v.title = response['snippet']['title']
    v.ytid = response['id']
    unique_slugify(v, v.title)
    v.published_on = isodate.parse_datetime(response['snippet']['publishedAt'])
    
    # get duration of video
    duration = response["contentDetails"]["duration"]
    v.duration = int(isodate.parse_duration(duration).total_seconds())
    
    # get description of video
    try:
        v.description = response['snippet']['description']
    except:
        pass

    # get category
    try:
        category_response = youtube_api.videoCategories().list(part="snippet",id=response['snippet']['categoryId']).execute()
        v.category = category_response.get("items", [])[0]['snippet']['title']
    except:
        pass

    # get thumbnail - "default"
    try:
        v.thumbnail = response['snippet']['thumbnails']['default']['url']
    except:
        pass

    # get view count
    try:
        v.views = int(response['statistics']['viewCount'])
    except:
        pass

    v.save()
    return v


def get_save_video_details(ytid):
    """
    Returns Video object for given ytid. Creates it if needed.
    """
    try:
        v = Video.objects.get(ytid=ytid)
    except Video.DoesNotExist:
        response = youtube_api.videos().list(id=ytid, part="id,snippet,contentDetails,statistics").execute()
        v = save_obj_from_entry(response.get("items", [])[0])
    return v


def search_for_videos(search_terms, page=1, catsearch=False):
    """
    Updated version of search_for_videos which provides v3 of Youtube API
    """
    try:
        key = base64.b64encode("ytsearch-%s-%s-%s" %(search_terms, page, catsearch))
    except:
        # got unicode errors occasionally
        search_terms = search_terms.encode("utf8")
        key = base64.b64encode("ytsearch-%s-%s-%s" %(search_terms, page, catsearch))

    output = cache.get(key)
    
    if output is None:
        output = {}

        pageToken = None
        page_index = 0
        while page_index < page:
            if not pageToken:
                search_response = youtube_api.search().list(
                    q = search_terms,
                    type="video",
                    part = "id",
                    maxResults = 12
                ).execute()
                pageToken = search_response.get("nextPageToken")
            else:
                search_response = youtube_api.search().list(
                    q = search_terms,
                    type="video",
                    part = "id",
                    pageToken = pageToken,
                    maxResults = 12
                ).execute()
                pageToken = search_response.get("nextPageToken")
            page_index += 1

        pageInfo = search_response.get("pageInfo")

        total = pageInfo.get("totalResults")
        if total > 1000:
            total = 1000

        results = []
        for search_result in search_response.get("items", []):
            results.append(get_save_video_details(search_result["id"]["videoId"]))
        
        output["results"] = results
        output["total"] = total
        cache.set(key, output, 1 * 60 * 60)
    else:
        total = output["total"]
        results = output["results"]
    return results, total

