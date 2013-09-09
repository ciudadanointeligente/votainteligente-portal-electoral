from django.db import models
from autoslug import AutoSlugField
from taggit.managers import TaggableManager
from candideitorg.models import Election as CanElection, Candidate as CanCandidate
from django.core.urlresolvers import reverse
from popit.models import Person, ApiInstance as PopitApiInstance
from django.db.models.signals import post_save
from django.dispatch import receiver

class Election(models.Model):
	name = models.CharField(max_length=255)
	slug = AutoSlugField(populate_from='name', unique=True)
	description = models.TextField()
	tags = TaggableManager()
	can_election = models.OneToOneField(CanElection, null=True)
	searchable = models.BooleanField(default=True)
	highlighted = models.BooleanField(default=False)
	popit_api_instance = models.OneToOneField(PopitApiInstance, null=True)


	def __unicode__(self):
		return self.name

	def get_absolute_url(self):
		return reverse('election_view', kwargs={'slug':self.slug})


class CandidatePerson(models.Model):
	person = models.OneToOneField(Person, related_name="relation")
	candidate = models.OneToOneField(CanCandidate, related_name="relation")


@receiver(post_save, sender=CanElection)
def automatically_create_election(sender, instance, created, **kwargs):
	can_election = instance
	if(created):
		Election.objects.create(
	            description = can_election.description,
	            can_election=can_election,
	            name = can_election.name,
	            )