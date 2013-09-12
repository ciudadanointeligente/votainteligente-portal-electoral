from django.db import models
from autoslug import AutoSlugField
from taggit.managers import TaggableManager
from candideitorg.models import Election as CanElection
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from markdown_deux.templatetags.markdown_deux_tags import markdown_allowed

class Election(models.Model):
	name = models.CharField(max_length=255)
	slug = AutoSlugField(populate_from='name', unique=True)
	description = models.TextField()
	tags = TaggableManager()
	can_election = models.ForeignKey(CanElection, null=True)
	searchable = models.BooleanField(default=True)
	highlighted = models.BooleanField(default=False)
	extra_info_title = models.CharField(max_length = 50, blank = True, null = True)
	extra_info_content = models.TextField(max_length = 3000, blank = True, null = True, help_text=_("Puedes usar Markdown. <br/> ") 
            + markdown_allowed())


	def __unicode__(self):
		return self.name

	def get_absolute_url(self):
		return reverse('election_view', kwargs={'slug':self.slug})
	def get_extra_info_url(self):
			return reverse('election_extra_info', kwargs={'slug':self.slug})
