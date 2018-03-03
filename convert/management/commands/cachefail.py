from django.core.management.base import BaseCommand, CommandError
import httplib2, json, random, boto, tempfile
from django.conf import settings
from convert.downloader import downloadvid, YoutubeException
from operator import itemgetter
from time import sleep

class Command(BaseCommand):
    """
    This management command will try to fetch failed videos into S3
    """
    def handle(self, *args, **options):
        conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        self.bucket = conn.get_bucket(settings.S3_YT_RAW_BUCKET)
        allpendings = self.get_pending()
        pendinglist = []
        for key in allpendings.keys():
            pendinglist += [{"yt_id": key,
            "count" : allpendings[key]}]
        newlist = sorted(pendinglist, key=itemgetter('count'))
        newlist.reverse()
        #print newlist
        print "Total %s videos remaining" %(len(newlist))
        for item in newlist:
            if self.checkexists(item["yt_id"]):
                print "%s already Exists in S3" %(item["yt_id"])
            else:
                print "downloading: %s, server tried %s times" %(item["yt_id"], item["count"])
                self.download(item["yt_id"])

    def download(self, yt_id):
        try:
            downloadvid(yt_id, tmppath=tempfile.gettempdir(), deletewhendone=True)
            print "Video %s downloaded successfully!" %(yt_id)
        except YoutubeException, err:
            print err


    def get_pending(self):
        h = httplib2.Http()
        r, c = h.request("http://www.getaudiofromvideo.com/getpending/?t=%s" %(random.randint(0,100000)))
        try:
            return json.loads(c)
        except:
            print c
            raise

    def checkexists(self, ytid):
        try:
            result = self.bucket.get_key(ytid) is not None
        except:
            sleep(5)
            result = self.bucket.get_key(ytid) is not None
        return result
