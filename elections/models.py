# coding=utf-8
from django.db import models
from autoslug import AutoSlugField
from taggit.managers import TaggableManager
from django.core.urlresolvers import reverse
from popolo.models import Person, Area
from django.utils.translation import ugettext_lazy as _
from markdown_deux.templatetags.markdown_deux_tags import markdown_allowed
from candidator.models import Category, Topic as CanTopic, TakenPosition
from picklefield.fields import PickledObjectField
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.flatpages.models import FlatPage
import copy
from writeit.models import Message
from elections import get_writeit_instance
from django.contrib.sites.models import Site
from django.db.models import Q, Count


class ExtraInfoMixin(models.Model):
    extra_info = PickledObjectField(default={})

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(ExtraInfoMixin, self).__init__(*args, **kwargs)
        default_extra_info = copy.copy(self.default_extra_info)
        default_extra_info.update(self.extra_info)
        self.extra_info = default_extra_info


class Candidate(Person, ExtraInfoMixin):
    election = models.ManyToManyField('Election', related_name='candidates', null=True)
    force_has_answer = models.BooleanField(default=False,
                                           help_text=_('Marca esto si quieres que el candidato aparezca como que no ha respondido'))

    default_extra_info = settings.DEFAULT_CANDIDATE_EXTRA_INFO

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
    uses_preguntales = models.BooleanField(default=False, help_text=_(u"Esta elección debe usar preguntales?"))
    uses_ranking = models.BooleanField(default=False, help_text=_(u"Esta elección debe usar ranking"))
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


class VotaInteligenteMessageManager(models.Manager):
    def get_queryset(self):
        queryset = super(VotaInteligenteMessageManager, self).get_queryset().annotate(num_answers=Count('answers'))
        return queryset.order_by('-num_answers', '-moderated', '-created')


@python_2_unicode_compatible
class VotaInteligenteMessage(Message):
    moderated = models.NullBooleanField(default=None)
    election = models.ForeignKey(Election, related_name='messages', default=None)
    created = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()
    ordered = VotaInteligenteMessageManager()

    class Meta:
        verbose_name = _(u'Mensaje de preguntales')
        verbose_name_plural = _(u'Mensajes de preguntales')

    def __str__(self):
        return u'%(author_name)s preguntó "%(subject)s" en %(election)s' % {'author_name': self.author_name,
                                                                            'subject': self.subject,
                                                                            'election': self.election.name
                                                                             }

    def accept_moderation(self):
        self.moderated = True
        self.save()

    def save(self, *args, **kwargs):

        if self.api_instance_id is None or self.writeitinstance_id is None:
            writeit_instance = get_writeit_instance()
            self.api_instance = writeit_instance.api_instance
            self.writeitinstance = writeit_instance
        super(VotaInteligenteMessage, self).save(*args, **kwargs)

    def get_absolute_url(self):
        election = self.election
        path = reverse('message_detail', kwargs={'election_slug': election.slug, 'pk': self.id})
        site = Site.objects.get_current()
        return "http://%s%s" % (site.domain, path)

    @classmethod
    def push_moderated_messages_to_writeit(cls):
        query = Q(moderated=True) & Q(remote_id=None)
        messages = VotaInteligenteMessage.objects.filter(query)
        for message in messages:
            message.push_to_the_api()

    def reject_moderation(self):
        self.moderated = True
        self.save()


class VotaInteligenteAnswer(models.Model):
    message = models.ForeignKey(VotaInteligenteMessage, related_name='answers')
    content = models.TextField()
    created = models.DateTimeField(editable=False, auto_now_add=True)
    person = models.ForeignKey(Candidate, related_name='answers')
