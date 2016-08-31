# coding=utf-8
from django.db import models
from autoslug import AutoSlugField
from taggit.managers import TaggableManager
from django.core.urlresolvers import reverse
from popolo.models import Person, Area as PopoloArea
from django.utils.translation import ugettext_lazy as _
from markdown_deux.templatetags.markdown_deux_tags import markdown_allowed
from candidator.models import Category, Topic as CanTopic, TakenPosition
from picklefield.fields import PickledObjectField
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.flatpages.models import FlatPage
import copy
from votainteligente.open_graph import OGPMixin


class Area(PopoloArea, OGPMixin):

    class Meta:
        proxy = True

    def get_absolute_url(self):
        return reverse('area', kwargs={'slug': self.id})

    @property
    def elections_without_position(self):
        return self.elections.filter(position__isnull=True).filter(position__exact='')


class ExtraInfoMixin(models.Model):
    extra_info = PickledObjectField(default={})

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(ExtraInfoMixin, self).__init__(*args, **kwargs)
        default_extra_info = copy.copy(self.default_extra_info)
        default_extra_info.update(self.extra_info)
        self.extra_info = default_extra_info


class Candidate(Person, ExtraInfoMixin, OGPMixin):
    elections = models.ManyToManyField('Election', related_name='candidates', default=None)
    force_has_answer = models.BooleanField(default=False,
                                           help_text=_('Marca esto si quieres que el candidato aparezca como que no ha respondido'))

    default_extra_info = settings.DEFAULT_CANDIDATE_EXTRA_INFO

    ogp_enabled = True

    @property
    def election(self):
        if self.elections.count() == 1:
            return self.elections.get()

    @property
    def twitter(self):
        links = self.contact_details.filter(contact_type="TWITTER")
        if links:
            return links.first()

    @property
    def has_answered(self):
        if self.force_has_answer:
            return False
        are_there_answers = TakenPosition.objects.filter(person=self, position__isnull=False).exists()
        return are_there_answers

    def get_absolute_url(self):
        election_slug = ''
        if self.election:
            election_slug = self.election.slug
        return reverse('candidate_detail_view', kwargs={
            'election_slug': election_slug,
            'slug': self.id
        })

    class Meta:
        verbose_name = _("Candidato")
        verbose_name_plural = _("Candidatos")


class CandidateFlatPage(FlatPage):
    candidate = models.ForeignKey(Candidate, related_name='flatpages')

    class Meta:
        verbose_name = _(u"Página estáticas por candidato")
        verbose_name_plural = _(u"Páginas estáticas por candidato")

    def get_absolute_url(self):
        return reverse('candidate_flatpage', kwargs={'election_slug': self.candidate.election.slug,
                                                     'slug': self.candidate.id,
                                                     'url': self.url
                                                     }
                       )


class PersonalData(models.Model):
    candidate = models.ForeignKey('Candidate', related_name="personal_datas")
    label = models.CharField(max_length=512)
    value = models.CharField(max_length=1024)


@python_2_unicode_compatible
class Topic(CanTopic):
    class Meta:
        proxy = True
        verbose_name = _(u"Pregunta")
        verbose_name_plural = _(u"Preguntas")

    @property
    def election(self):
        category = QuestionCategory.objects.get(category_ptr=self.category)
        return category.election

    def __str__(self):
        return u'<%s> en <%s>' % (self.label, self.election.name)


@python_2_unicode_compatible
class QuestionCategory(Category):
    election = models.ForeignKey('Election', related_name='categories', null=True)

    def __str__(self):
        return u'<%s> in <%s>' % (self.name, self.election.name)

    class Meta:
        verbose_name = _(u"Categoría de pregunta")
        verbose_name_plural = _(u"Categorías de pregunta")


class Election(ExtraInfoMixin, models.Model, OGPMixin):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from='name', unique=True)
    description = models.TextField(blank=True)
    tags = TaggableManager(blank=True)
    searchable = models.BooleanField(default=True)
    highlighted = models.BooleanField(default=False)
    extra_info_title = models.CharField(max_length=50, blank=True, null=True)
    extra_info_content = models.TextField(max_length=3000, blank=True, null=True, help_text=_("Puedes usar Markdown. <br/> ")
            + markdown_allowed())
    uses_preguntales = models.BooleanField(default=False, help_text=_(u"Esta elección debe usar preguntales?"))
    uses_ranking = models.BooleanField(default=False, help_text=_(u"Esta elección debe usar ranking"))
    uses_face_to_face = models.BooleanField(default=True, help_text=_(u"Esta elección debe usar frente a frente"))
    uses_soul_mate = models.BooleanField(default=True, help_text=_(u"Esta elección debe usar 1/2 naranja"))
    uses_questionary = models.BooleanField(default=True, help_text=_(u"Esta elección debe usar cuestionario"))
    position = models.CharField(default='',
                                null=True,
                                blank=True,
                                max_length=255,
                                help_text=_(u'A qué cargo está postulando?'))

    default_extra_info = settings.DEFAULT_ELECTION_EXTRA_INFO
    area = models.ForeignKey(Area, blank=True, null=True, related_name="elections")

    ogp_enabled = True

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('election_view', kwargs={'slug': self.slug})

    def get_extra_info_url(self):
            return reverse('election_extra_info', kwargs={'slug': self.slug})

    class Meta:
            verbose_name = _(u'Mi Elección')
            verbose_name_plural = _(u'Mis Elecciones')
