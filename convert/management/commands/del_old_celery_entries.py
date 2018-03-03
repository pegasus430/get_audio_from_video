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
        from djcelery.models import TaskState
        from datetime import datetime,timedelta
        TIME_TO_KEEP = 2 # hours
        _time = datetime.now() - timedelta(hours=TIME_TO_KEEP)
        TaskState.objects.filter(tstamp__lte=_time).delete()

        # remove every records whose state is "STARTED", but not finished for 2 hours
        from celery.task.control import revoke
        two_days = 7200 # 2 hours in seconds
        for task in TaskState.objects.expired(['STARTED'], two_days):
            self.stdout.write(task.task_id)
            self.stdout.write(task.name)
            self.stdout.write(task.tstamp)
            revoke(task.task_id, terminate=True)
            break


