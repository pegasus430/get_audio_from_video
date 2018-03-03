import subprocess, random, os
from django.conf import settings
import boto, random
from boto.s3.key import Key

class YoutubeException(Exception):
    pass

def checkexists(ytid, bucketname):
    conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(bucketname)
    cached_file = bucket.get_key(ytid)
    return (cached_file is not None) and (cached_file.size != 0)

def downloadvid(ytid, taskid=None, yt_path=os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/external/youtube-dl", tmppath="/mnt", deletewhendone=False):
    if taskid is None:
        taskid=random.randint(1, 100000)
    filename = "%s/%s" %(tmppath, taskid)
    print yt_path
    p = subprocess.Popen([yt_path, "http://www.youtube.com/watch?v=%s" %(ytid), "-f", "18", "-o", taskid ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=tmppath)
    com = p.communicate()
    output = com[0]
    #tmpfile =  output.split("Destination: ")[1].split('\n')[0]
    tmpfile = filename
    print tmpfile
    success = os.path.isfile(tmpfile)
    print success
    if success == False:
        #Download failed... lets retry without setting format
        p = subprocess.Popen([yt_path, "http://www.youtube.com/watch?v=%s" %(ytid), "-o", taskid ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=tmppath)
        com = p.communicate()
        output = com[0]
        #tmpfile =  output.split("Destination: ")[1].split('\n')[0]
        tmpfile = filename
    #Recheck if download was successfull and raise error accordingly
    if not os.path.isfile(tmpfile):
        debugoutput = ""
        for line in com:
            debugoutput += line
        #raise YoutubeException(debugoutput)
        return False, debugoutput

    #recheck if file in S3. may have been uploaded by some other process
    conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(settings.S3_YT_RAW_BUCKET)
    
    print ytid
    if bucket.get_key(ytid) is None:
    #now upload it to s3    
        k = Key(bucket)
        k.key = ytid
        k.set_contents_from_filename(tmpfile)
        newfile = bucket.get_key(k.key)
        newfile.change_storage_class('REDUCED_REDUNDANCY')
    
    if deletewhendone:
        try:
            os.remove(tmpfile)
        except:
            pass
    return True, ""

    #print filename


#if __name__ == "__main__":
#    downloadvid("dVKVNmvQmBc")
