from django.db import models
from autoslug import AutoSlugField
from categories.models import Category


class Election(models.Model):
	name = models.CharField(max_length=255)
	slug = AutoSlugField(populate_from='name', unique=True)
	description = models.TextField()
	category = models.OneToOneField(Category, related_name='election', null=True)