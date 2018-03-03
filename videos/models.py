from django.db import models

# Create your models here.

class Video(models.Model):
    title = models.CharField(max_length=200, help_text="Title of the current video")
    ytid = models.CharField(unique=True, max_length=20, help_text="Youtube ID", db_index=True)
    slug = models.SlugField(max_length=200, unique=True, help_text="To make the url of the current video page")
    duration = models.IntegerField(help_text="Duration of the video in seconds")
    description = models.TextField(null=True, blank=True, help_text="Video Description")
    published_on = models.DateTimeField(help_text="Date the video was published")
    rating = models.FloatField(null=True, blank=True, help_text="Duration of the video in seconds")
    thumbnail = models.URLField(null=True, blank=True, help_text="thumbnail from youtube")
    views = models.IntegerField(help_text="number of views the video has had", null=True, blank=True)
    related = models.CharField(max_length=100, help_text="Youtube IDs of related videos", null=True, blank=True)
    category = models.CharField(max_length=40, help_text="Video Category", null=True, blank=True)
    last_modified = models.DateTimeField(auto_now=True, help_text="Time when model was last updated/created")
    last_converted = models.DateTimeField(help_text="Time when video had last conversion request", null=True, blank=True, db_index=True)

    def __unicode__(self):
        return "<%s> %s" %(self.ytid, self.title)

    def get_absolute_url(self):
        return "/videos/%s/" %(self.slug)

    def get_end_time(self):
        minutes = int(self.duration/60)
        seconds = (self.duration - minutes * 60)
        if minutes < 10:
            minutes = "0%d" % minutes
        if seconds < 10:
            seconds = "0%d" % seconds
        return "%s:%s" %(minutes, seconds)

    def get_description(self):
        if self.description is not None:
            return self.description
        else:
            return ""
