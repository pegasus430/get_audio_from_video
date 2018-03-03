from celery.task import task
from convert.downloader import downloadvid, checkexists, YoutubeException
from convert.converter import convertvid
from celery.execute import send_task
from celery.result import AsyncResult
import base64, os, boto
from boto.s3.key import Key
from django.conf import settings
from urllib import quote
import md5
import time

@task(name="tasks.fetchandconvert")
def fetchandconvert(options):
    print options
    fetchandconvert.update_state(state="STARTING", meta={"progress": 0})
    id3 = None
    if options["format"] == "mp3":
        #Only need id3 if mp3
        id3 = {
            "title": options["ID3_title"],
            "tracknumber": options["ID3_track_no"],
            "date": options["ID3_year"],
            "album": options["ID3_album"],
            "artist": options["ID3_artist"],
            "genre": options["ID3_genre"],
        }
    key = md5.new(str(options['ytid']) + str(options['transcoder_quality']) + str(id3) + str(options["youtube_start"]) + str(options["youtube_end"])).hexdigest()
    convertedname = "%s.%s" %(base64.b64encode(key), options["format"])
    finalfile = "%s/%s.%s" %(fetchandconvert.request.id , options["filename"], options["format"])
    requestedfilename = options["filename"] + "." + options["format"]
    fetchandconvert.update_state(state="DOWNLOADING", meta={"progress": 5})
    #Step 1: check is conversion is already ready
    if not checkexists(convertedname, settings.S3_YT_PRO_BUCKET):
        print "%s not in cache" %(convertedname)
        task_id = fetchandconvert.request.id
        print task_id
        #Step 2 , check if raw file is in s3, if not then download into s3 (new task)
        if not checkexists(options["ytid"], settings.S3_YT_RAW_BUCKET):
            print "%s not in S3 so downloading..." %(options["ytid"])
            # we will use a new task to do the download
            #is_succ, msg = downloadvid(options["ytid"], task_id)
            options.update({"task_id" : task_id })
            is_succ, msg = downloadvid(options["ytid"], task_id)
            if not is_succ:
                # create a new task
                # after the new task, the video should be stored in S3
                t = send_task("tasks.youtubedl_alt1", [options])
                result = AsyncResult(t.task_id)
                TIMES = 10
                current_time = 1
                while result.status not in ["SUCCESS", "FAILURE"]:
                    if current_time > TIMES:
                        break
                    print result.status
                    time.sleep(3)    # sleep 3 seconds to let another worker handle the task
                    result = AsyncResult(t.task_id)
                    current_time += 1
                fetchandconvert.update_state(state="FAILURE", meta={"progress": 30, 
                        "traceback" : msg, "status" : "FAILURE"})
                raise YoutubeException(msg)
                
        print "back to the fetchandconvert"
        fetchandconvert.update_state(state="CONVERTING", meta={"progress": 30})
        convertvid(options["ytid"], options, convertedname, task_id, fetchandconvert, options["duration"], id3)
    # Cleanup
    fetchandconvert.update_state(state="CLEANUP", meta={"progress": 90})
    try:
        os.remove("/mnt/" + task_id)
    except:
        pass
    try:
        os.remove("/mnt/" + convertedname)
    except:
        pass
    try:
        os.remove("/mnt/" + task_id + ".mp4")
    except:
        pass
    #Setp 3: Generate and return signed temporary URL
    fetchandconvert.update_state(state="SIGNING", meta={"progress": 95})
    conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(settings.S3_YT_PUB_BUCKET)
    bucket.copy_key(finalfile, settings.S3_YT_PRO_BUCKET, convertedname)
    k = Key(bucket)
    k.key = finalfile
    k.change_storage_class('REDUCED_REDUNDANCY')
#    new_headers = {'response-content-disposition': 'attachment;filename=' + requestedfilename }
    if options["format"] == "m4r":
        import urllib
        new_headers = {'response-content-disposition': 'attachment;filename=%s' % urllib.quote(requestedfilename)}
    else:
        new_headers = {'response-content-disposition': 'attachment'}
    url = conn.generate_url(900 , 'GET', bucket=settings.S3_YT_PUB_BUCKET, key = finalfile, response_headers = new_headers)
    print url
    return {"url": url}

@task(name="tasks.youtubedl_default")
def youtubedl_default(options):
    print options
    task_id = youtubedl_default.request.id
    youtubedl_default.update_state(state="STARTING", meta={"progress":0})
    is_succ, msg = downloadvid(options["ytid"], options["task_id"])
    if not is_succ:
        send_task("tasks.youtubedl_alt1", [options])

@task(name="tasks.youtubedl_alt1")
def youtubedl_alt1(options):
    print options
    task_id = youtubedl_alt1.request.id
    youtubedl_alt1.update_state(state="STARTING", meta={"progress":0})
    is_succ, msg = downloadvid(options["ytid"], options["task_id"])
    if not is_succ:
        youtubedl_alt1.update_state(state="FAILURE", meta={"progress":0})
        raise YoutubeException(msg)

# youtubedl_alt2 is not used for now
@task(name="tasks.youtubedl_alt2", ignore_result=True)
def youtubedl_alt2(options):
    task_id = youtubedl_alt2.request.id
    youtubedl_alt2.update_state(state="STARTING", meta={"progress":0})
    is_succ, msg = downloadvid(options["ytid"], options["task_id"])
    if not is_succ:
        send_task("tasks.youtubedl_alt1", [options])
