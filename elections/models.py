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
from django.db.models import Count, F, FloatField, ExpressionWrapper
from django.shortcuts import render
from constance import config

class AreaManager(models.Manager):
    def get_queryset(self):
        return super(AreaManager, self).get_queryset().exclude(id__in=config.HIDDEN_AREAS)


def get_position_in_(qs, el):
    position = 0
    for c in qs:
        position += 1
        if el == c:
            return position

class Area(PopoloArea, OGPMixin):
    public = AreaManager()

    class Meta:
        proxy = True

    def get_absolute_url(self):
        return reverse('area', kwargs={'slug': self.id})

    def ogp_description(self):
        return self.name

    @property
    def elections_without_position(self):
        return self.elections.filter(position__isnull=True).filter(position__exact='')

    def candidates(self):
        return Candidate.objects.filter(elections__area=self)


class ExtraInfoMixin(models.Model):
    extra_info = PickledObjectField(default={})

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(ExtraInfoMixin, self).__init__(*args, **kwargs)
        default_extra_info = copy.copy(self.default_extra_info)
        default_extra_info.update(self.extra_info)
        self.extra_info = default_extra_info


class HaveAnsweredFirst(models.Manager):
    def get_queryset(self):
        qs = super(HaveAnsweredFirst, self).get_queryset().annotate(num_answers=Count('taken_positions'))
        qs = qs.order_by('-num_answers', '-image')
        return qs

class WinnersFirst(models.Manager):
    def get_queryset(self):
        qs = super(WinnersFirst, self).get_queryset().annotate(num_answers=Count('taken_positions'))
        qs = qs.order_by('has_won', '-num_answers')
        return qs

class RankingManager(models.Manager):
    def get_queryset(self):
        qs = super(RankingManager, self).get_queryset()
        qs = qs.annotate(possible_answers=Count(F('elections__categories__topics'), distinct=True))
        qs = qs.annotate(num_answers=Count('taken_positions', distinct=True))
        qs = qs.annotate(naranja_completeness=ExpressionWrapper((F('num_answers') * 1.0 / F('possible_answers') * 1.0) * 100,
                                                                output_field=FloatField()))

        qs = qs.annotate(num_proposals=Count(F('elections__area__proposals'), distinct=True))
        qs = qs.annotate(num_commitments=Count(F('commitments'), distinct=True))
        qs = qs.annotate(commitmenness=ExpressionWrapper((F('num_commitments') * 1.0 / F('num_proposals') * 1.0) * 100,
                                                                output_field=FloatField()))

        # This can be a bit tricky
        # and it is the sum of the percentage of completeness of 1/2 naranja and the commitmenness
        qs = qs.annotate(participation_index=ExpressionWrapper(F('naranja_completeness') + F('commitmenness'),
                                                                output_field=FloatField()))
        qs = qs.order_by('-has_won', '-participation_index')
        return qs

    def position(self, candidate):
        qs = self.get_queryset()
        return get_position_in_(qs, candidate)

class Candidate(Person, ExtraInfoMixin, OGPMixin):
    elections = models.ManyToManyField('Election', related_name='candidates', default=None)
    force_has_answer = models.BooleanField(default=False,
                                           help_text=_('Marca esto si quieres que el candidato aparezca como que no ha respondido'))

    has_won = models.BooleanField(default=False)

    default_extra_info = settings.DEFAULT_CANDIDATE_EXTRA_INFO

    objects = HaveAnsweredFirst()
    answered_first = HaveAnsweredFirst()
    ranking = RankingManager()

    ogp_enabled = True

    @property
    def election(self):
        if self.elections.count() == 1:
            return self.elections.get()

    @property
    def twitter(self):
        links = self.contact_details.filter(contact_type="TWITTER")
        if links.exists():
            return links.first()

    def facebook(self):
        links = self.contact_details.filter(contact_type="FACEBOOK")
        if links:
            return links.first()

    def has_logged_in(self):
        if self.candidacy_set.filter(user__last_login__isnull=True).exists():
            return False
        return True

    def possible_answers(self):
        return Topic.objects.filter(category__in=self.election.categories.all())

    @property
    def has_answered(self):
        if self.force_has_answer:
            return False
        are_there_answers = TakenPosition.objects.filter(person=self, position__isnull=False).exists()
        return are_there_answers

    def has_joined(self):
        if self.candidacy_set.exclude(user__last_login__isnull=True):
            return True
        return False

    def ranking_in_election(self):
        if self.election:
            return self.election.position_in_ranking(self)

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
    value = models.CharField(max_length=4096)


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

    def ranking(self):
        return Candidate.ranking.filter(elections=self)

    def position_in_ranking(self, candidate):
        qs = self.ranking()
        return get_position_in_(qs, candidate)

    def get_extra_info_url(self):
            return reverse('election_extra_info', kwargs={'slug': self.slug})

    def has_anyone_answered(self):
        return TakenPosition.objects.filter(person__in=self.candidates.all()).exists()

    class Meta:
            verbose_name = _(u'Mi Elección')
            verbose_name_plural = _(u'Mis Elecciones')
