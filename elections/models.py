# coding=utf-8
from django.db import models
from autoslug import AutoSlugField
from taggit.managers import TaggableManager
from django.core.urlresolvers import reverse
from popolo.models import Person, Area
from django.utils.translation import ugettext as _
from markdown_deux.templatetags.markdown_deux_tags import markdown_allowed
from candidator.models import Category, Topic as CanTopic
from picklefield.fields import PickledObjectField
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible


class ExtraInfoMixin(models.Model):
    extra_info = PickledObjectField(default={})

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(ExtraInfoMixin, self).__init__(*args, **kwargs)
        default_extra_info = self.default_extra_info
        default_extra_info.update(self.extra_info)
        self.extra_info = default_extra_info


class Candidate(Person, ExtraInfoMixin):
    election = models.ForeignKey('Election', related_name='candidates', null=True)

    default_extra_info = settings.DEFAULT_CANDIDATE_EXTRA_INFO

    @property
    def twitter(self):
        links = self.contact_details.filter(contact_type="TWITTER")
        if links:
            return links.first()


class PersonalData(models.Model):
    candidate = models.ForeignKey('Candidate', related_name="personal_datas")
    label = models.CharField(max_length=512)
    value = models.CharField(max_length=1024)


class Topic(CanTopic):
    class Meta:
        proxy = True

    @property
    def election(self):
        category = QuestionCategory.objects.get(category_ptr=self.category)
        return category.election


@python_2_unicode_compatible
class QuestionCategory(Category):
    election = models.ForeignKey('Election', related_name='categories', null=True)

    def __str__(self):
        return u'<%s> in <%s>' % (self.name, self.election.name)


class Election(ExtraInfoMixin, models.Model):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from='name', unique=True)
    description = models.TextField(blank=True)
    tags = TaggableManager(blank=True)
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

    default_extra_info = settings.DEFAULT_ELECTION_EXTRA_INFO
    area = models.ForeignKey(Area, null=True, related_name="elections")

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('election_view', kwargs={'slug': self.slug})

    def get_extra_info_url(self):
            return reverse('election_extra_info', kwargs={'slug': self.slug})

    class Meta:
            verbose_name = _(u'Mi Elección')
            verbose_name_plural = _(u'Mis Elecciones')
