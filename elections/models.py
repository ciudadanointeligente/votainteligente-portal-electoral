from django.db import models
from autoslug import AutoSlugField
from taggit.managers import TaggableManager


class Election(models.Model):
	name = models.CharField(max_length=255)
	slug = AutoSlugField(populate_from='name', unique=True)
	description = models.TextField()
	tags = TaggableManager()


	def __unicode__(self):
		return self.name