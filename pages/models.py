from django.db import models
from django.core.cache import cache

# Create your models here.

class Page(models.Model):
	title = models.CharField(max_length=200, help_text="Title of the page")
	slug = models.SlugField(max_length=200, unique=True, help_text="url portion")
	desc = models.TextField(help_text="Meta Description")
	body = models.TextField(help_text="HTML body contents")
	weight = models.IntegerField(help_text="lower number shows higher in menus, set 0 to not show in menus", default=0)
	menu_name = models.CharField(null=True, blank=True, max_length=200, help_text="To show in menu, if blank uses title")
	link_override = models.CharField(null=True, blank=True, max_length=200, help_text="If present, page links to this url instead")

	def __unicode__(self):
		return "%s: %s" %(self.slug, self.title)

	def get_absolute_url(self):
		if self.link_override is not None:
			if len(self.link_override) > 1:
				return self.link_override
		return "/%s/" %(self.slug)

	def get_menu_name(self):
		if self.menu_name is not None:
			if len(self.menu_name) > 0:
				return self.menu_name
		return self.title

	def save(self, *args, **kwargs):
		super(Page, self).save(*args, **kwargs)
		#clear cache when page is being saved
		cache.clear()