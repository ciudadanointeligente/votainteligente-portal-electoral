# coding=utf-8
from django.db import models
from autoslug import AutoSlugField
from taggit.managers import TaggableManager
from candideitorg.models import Election as CanElection, Candidate as CanCandidate
from django.core.urlresolvers import reverse
from popolo.models import Person
from django.utils.translation import ugettext as _
from markdown_deux.templatetags.markdown_deux_tags import markdown_allowed
from candidator.models import Category
import re


class Candidate(Person):
    election = models.ForeignKey('Election', related_name='candidates', null=True)


class QuestionCategory(Category):
    election = models.ForeignKey('Election', related_name='categories', null=True)


class Election(models.Model):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from='name', unique=True)
    description = models.TextField(blank=True)
    tags = TaggableManager(blank=True)
    can_election = models.OneToOneField(CanElection, null=True, blank=True)
    searchable = models.BooleanField(default=True)
    highlighted = models.BooleanField(default=False)
    extra_info_title = models.CharField(max_length=50, blank=True, null=True)
    extra_info_content = models.TextField(max_length=3000, blank=True, null=True, help_text=_("Puedes usar Markdown. <br/> ")
            + markdown_allowed())
    uses_preguntales = models.BooleanField(default=True, help_text=_(u"Esta elección debe usar preguntales?"))
    uses_ranking = models.BooleanField(default=True, help_text=_(u"Esta elección debe usar ranking"))
    uses_face_to_face = models.BooleanField(default=True, help_text=_(u"Esta elección debe usar frente a frente"))
    uses_soul_mate = models.BooleanField(default=True, help_text=_(u"Esta elección debe usar 1/2 naranja"))
    uses_questionary = models.BooleanField(default=True, help_text=_(u"Esta elección debe usar cuestionario"))

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('election_view', kwargs={'slug': self.slug})

    def get_extra_info_url(self):
            return reverse('election_extra_info', kwargs={'slug': self.slug})

    class Meta:
            verbose_name = _(u'Mi Elección')
            verbose_name_plural = _(u'Mis Elecciones')


class CandidatePerson(models.Model):
    person = models.OneToOneField(Person, related_name="relation")
    candidate = models.OneToOneField(CanCandidate, related_name="relation")
    reachable = models.BooleanField(default=False)
    description = models.TextField(default='', blank=True)
    portrait_photo = models.CharField(max_length=256, blank=True, null=True)
    custom_ribbon = models.CharField(max_length=18, blank=True, null=True)

    def __unicode__(self):
        return u'Extra info de %(candidate)s' % {
            "candidate": self.candidate.name
            }

    def _get_twitter_(self):
        try:
            twitter = self.candidate.link_set.filter(url__contains='twitter')[0].url
            regex = re.compile(r"^https?://(www\.)?twitter\.com/(#!/)?([^/]+)(/\w+)*$")
            return regex.match(twitter).groups()[2]
        except:
            return None
    twitter = property(_get_twitter_)

    class Meta:
            verbose_name = _(u'Extra Info de candidato')
            verbose_name_plural = _(u'Extra Info de candidatos')
