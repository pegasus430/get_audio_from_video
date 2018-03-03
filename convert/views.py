# Create your views here.
from django.http import HttpResponse
from celery.execute import send_task
from celery.result import AsyncResult
import json
import base64
from videos.models import Video
from datetime import datetime
from django.core.cache import cache
from collections import Counter
from  djcelery.models import TaskState
from convert.downloader import checkexists
from django.conf import settings

def getpending(request):
    cnt =  Counter([eval(i.args)[0]["ytid"] for i in TaskState.objects.filter(state="FAILURE").filter(traceback__contains="YoutubeException")])
    pending = {}
    for item, count in cnt.most_common(800):
        exists  = cache.get("exists" + item)
        if exists is None:
            try:
                exists = checkexists(item, settings.S3_YT_RAW_BUCKET)
                if exists:
                    cache.set("exists" + item, exists, 240 * 60 * 60)
                else:
                    cache.set("exists" + item, exists,  60 * 60)
            except:
                exists = False
        if not exists:
            pending[item] = count
    return HttpResponse(json.dumps(pending))

def islimited(request, iscontinue=False):
    """
    iscontinue flags whether this conversion is a "continuing conversion",
    if so, then won't consume the request time limit
    the return:
    islimited, current request time
    """
    logged = request.POST.get("logged", "false")
    memberstatus = request.POST.get("memberstatus", "false")
    delayed = request.POST.get("delayeduser", "1")
    if iscontinue:
        return False, 0
    if memberstatus == "true":
        return False, 0
    else:
        print request.META["REMOTE_ADDR"]
        key = base64.b64encode("newratelim" + request.META["REMOTE_ADDR"])
        limited = cache.get(key)
        if limited is None:
            cache.set(key, 1, 24 * 60 * 60)
            return False, 1
        elif limited < 3:
            cache.set(key, limited + 1, 24 * 60 * 60)
            return False, limited + 1
        else:
            return True, 0

def convert(request):
    if request.method == 'GET':
        id = request.GET.get("id", None)
        result = AsyncResult(base64.b64decode(id))
        if result.status == "SUCCESS":
            out = {"status": "SUCCESS", "result": result.result}
            return HttpResponse(json.dumps(out), mimetype='application/json')
        else:
            if result.status == "FAILURE":
                result_info = {"progress" : "5"}
            else:
                result_info = result.info
            return HttpResponse(json.dumps({"status": result.status, "info": result_info}), mimetype='application/json')
    elif request.method == 'POST':
        print request.POST
        iscontinue = request.POST.get("iscontinue")
        iscontinue = iscontinue == "true"
        taskid = request.POST.get("taskid", "")
        result = None
        need_new_task = True
        if taskid:
            from djcelery.models import TaskState
            rec = TaskState.objects.filter(task_id=base64.b64decode(taskid))
            if rec:
                need_new_task = rec[0].state == "FAILURE"
        #do rate limiting here
        limited, times = islimited(request, iscontinue)
        if limited:
            return HttpResponse(json.dumps({"id": "RATELIMIT"}), mimetype='application/json')
        elif not need_new_task:
            return HttpResponse(json.dumps({"id": taskid, "times" : times}), mimetype='application/json')
        else:
            options = {}
            options['ytid'] = request.POST.get("ytid")
            options['format'] = request.POST.get("format")
            options['filename'] = request.POST.get("outputfilename")
            options['transcoder_quality'] = request.POST.get("transcoder_quality")
            options['ID3_artist'] = request.POST.get("ID3_artist")
            options['ID3_album'] = request.POST.get("ID3_album")
            options['ID3_track_no'] = request.POST.get("ID3_track_no")
            options['ID3_year'] = request.POST.get("ID3_year")
            options['ID3_comment'] = request.POST.get("ID3_comment")
            options['ID3_genre'] = request.POST.get("ID3_genre")
            options['ID3_title'] = request.POST.get("ID3_title")
            options['youtube_start'] = request.POST.get("youtube_start")
            options['youtube_end'] = request.POST.get("youtube_end")
            v = Video.objects.get(ytid=options['ytid'])
            options['duration'] = v.duration
            options['username'] = request.POST.get("username", "None")
            # Since we support unlimited membershp, we need to remove the checking of duration
            #if v.duration > 3600:
                # source video is > 1 hour
            #    return HttpResponse(json.dumps({"id": "TOOLONG"}), mimetype='application/json')
            print options
            t =  send_task("tasks.fetchandconvert", [options])
            v.last_converted = datetime.now()
            v.save()
            if times != 0:
                return HttpResponse(json.dumps({"id": base64.b64encode(t.task_id), "times" : times}), mimetype='application/json')
            return HttpResponse(json.dumps({"id": base64.b64encode(t.task_id), "times" : 0}), mimetype='application/json')
