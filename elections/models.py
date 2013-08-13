from django.db import models
from autoslug import AutoSlugField


class Election(models.Model):
	name = models.CharField(max_length=255)
	slug = AutoSlugField(populate_from='name', unique=True)
	description = models.CharField(max_length=255)