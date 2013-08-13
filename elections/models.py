from django.db import models


class Election(models.Model):
	name = models.CharField(max_length=255)
	slug = models.CharField(max_length=255, unique=True)
	description = models.CharField(max_length=255)