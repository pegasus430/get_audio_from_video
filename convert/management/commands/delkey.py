from django.core.management.base import BaseCommand, CommandError
import httplib2, json, random, boto, tempfile
from django.conf import settings
from operator import itemgetter
from time import sleep

class Command(BaseCommand):
    """
    This management command will try to fetch failed videos into S3
    """
    def handle(self, *args, **options):
        ytid = args[0]
        conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        self.bucket = conn.get_bucket(settings.S3_YT_RAW_BUCKET)
        key = self.bucket.get_key(ytid)
        try:
            print "%s will be deleted" % str(key)
            key.delete()
        except:
            pass


