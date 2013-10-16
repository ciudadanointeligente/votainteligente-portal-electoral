# coding=utf-8
from django.db import models
from autoslug import AutoSlugField
from taggit.managers import TaggableManager
from candideitorg.models import Election as CanElection, Candidate as CanCandidate
from django.core.urlresolvers import reverse
from popit.models import Person, ApiInstance as PopitApiInstance
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils.translation import ugettext as _
from markdown_deux.templatetags.markdown_deux_tags import markdown_allowed
from writeit.models import WriteItApiInstance, WriteItInstance
from candideitorg.models import election_finished

class Election(models.Model):
	name = models.CharField(max_length=255)
	slug = AutoSlugField(populate_from='name', unique=True)
	description = models.TextField(blank=True)
	tags = TaggableManager(blank=True)
	can_election = models.OneToOneField(CanElection, null=True, blank=True)
	searchable = models.BooleanField(default=True)
	highlighted = models.BooleanField(default=False)
	popit_api_instance = models.OneToOneField(PopitApiInstance, null=True, blank=True)
	writeitinstance = models.OneToOneField(WriteItInstance, null=True, blank=True)
	extra_info_title = models.CharField(max_length = 50, blank = True, null = True)
	extra_info_content = models.TextField(max_length = 3000, blank = True, null = True, help_text=_("Puedes usar Markdown. <br/> ") 
            + markdown_allowed())


	def __unicode__(self):
		return self.name

	def get_absolute_url(self):
		return reverse('election_view', kwargs={'slug':self.slug})

	def get_extra_info_url(self):
			return reverse('election_extra_info', kwargs={'slug':self.slug})

	class Meta:
	        verbose_name = _(u'Mi Elección')
	        verbose_name_plural = _(u'Mis Elecciones')

	        
class CandidatePerson(models.Model):
	person = models.OneToOneField(Person, related_name="relation")
	candidate = models.OneToOneField(CanCandidate, related_name="relation")


@receiver(post_save, sender=CanElection)
def automatically_create_election(sender, instance, created, **kwargs):
	if kwargs.get('raw', False):
		return
	can_election = instance
	if(created):
		election = Election.objects.create(
	            description = can_election.description,
	            can_election=can_election,
	            name = can_election.name,
	            )

		if getattr(settings, 'USE_POPIT', True):
			popit_api_instance_url = settings.POPIT_API_URL% ( election.slug)

			popit_api_instance = PopitApiInstance.objects.create(
				url = popit_api_instance_url
				)
			election.popit_api_instance = popit_api_instance
			if getattr(settings, 'USE_WRITEIT', True):
				writeit_api_instance = get_current_writeit_api_instance()
				writeitinstance = WriteItInstance.objects.create(api_instance=writeit_api_instance, name=can_election.name)

				election.writeitinstance = writeitinstance
				election.save()




@receiver(post_save, sender=CanCandidate)
def automatically_create_popit_person(sender, instance, created, **kwargs):
	if kwargs.get('raw', False):
		return
	should_be_using_popit = getattr(settings, 'USE_POPIT', True)
	if not should_be_using_popit:
		return
	candidate = instance
	api_instance = candidate.election.election.popit_api_instance
	if created and api_instance:
		person = Person.objects.create(
			api_instance = api_instance,
			name=candidate.name
			)
		person.post_to_the_api()
		relation = CandidatePerson.objects.create(person=person, candidate=candidate)


@receiver(election_finished)
def automatically_push_writeit_instance(sender, instance, created, **kwargs):
	if kwargs.get('raw', False) or not created:
		return
	use_popit = getattr(settings, 'USE_POPIT', True)
	use_writeit = getattr(settings, 'USE_WRITEIT', True)
	if use_popit and use_writeit:

		election = Election.objects.get(can_election=instance)
		extra_params = {
		'popit-api': election.popit_api_instance.url
		}
		election.writeitinstance.push_to_the_api(extra_params=extra_params)



def get_current_writeit_api_instance():
	api_instance, created = WriteItApiInstance.objects.get_or_create(url=settings.WRITEIT_API_URL)
	return api_instance
