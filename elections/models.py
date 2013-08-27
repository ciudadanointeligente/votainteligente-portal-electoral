from django.db import models
from autoslug import AutoSlugField
from taggit.managers import TaggableManager
from candideitorg.models import Election as CanElection
from django.core.urlresolvers import reverse

class Election(models.Model):
	name = models.CharField(max_length=255)
	slug = AutoSlugField(populate_from='name', unique=True)
	description = models.TextField()
	tags = TaggableManager()
	can_election = models.ForeignKey(CanElection, null=True)
	searchable = models.BooleanField(default=True)
	highlighted = models.BooleanField(default=False)


	def __unicode__(self):
		return self.name

	def get_absolute_url(self):
		return reverse('election_view', kwargs={'slug':self.slug})
