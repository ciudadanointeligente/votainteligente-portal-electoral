# coding=utf-8
from django.db import models
from writeit.models import Message as WriteItMessage
from elections.models import Election, Candidate
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q, Count
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from autoslug import AutoSlugField
from django.core.mail import EmailMessage
from django.template import Context
from django.template.loader import get_template
from django.conf import settings


class MessageManager(models.Manager):
    def get_queryset(self):
        queryset = super(MessageManager, self).get_queryset().annotate(num_answers=Count('answers_'))
        return queryset.order_by('-num_answers', '-accepted', '-created')


@python_2_unicode_compatible
class Message(models.Model):
    author_name = models.CharField(max_length=256)
    author_email = models.EmailField(max_length=512)
    content = models.TextField()
    people = models.ManyToManyField(Candidate)
    subject = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from='subject', unique=True)
    accepted = models.NullBooleanField(default=None)
    sent = models.BooleanField(default=False)
    election = models.ForeignKey(Election, related_name='messages_', default=None)
    created = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()
    ordered = MessageManager()

    class Meta:
        verbose_name = _(u'Mensaje de preguntales')
        verbose_name_plural = _(u'Mensajes de preguntales')

    def __str__(self):
        return u'%(author_name)s preguntó "%(subject)s" en %(election)s' % {'author_name': self.author_name,
                                                                            'subject': self.subject,
                                                                            'election': self.election.name
                                                                             }

    def accept_moderation(self):
        self.accepted = True
        self.save()

    def save(self, *args, **kwargs):

        super(Message, self).save(*args, **kwargs)

    def get_absolute_url(self):
        election = self.election
        path = reverse('message_detail', kwargs={'election_slug': election.slug, 'pk': self.id})
        site = Site.objects.get_current()
        return "http://%s%s" % (site.domain, path)

    #@classmethod
    #def push_moderated_messages_to_writeit(cls):
    #    query = Q(moderated=True) & Q(remote_id=None)
    #    messages = Message.objects.filter(query)
    #    for message in messages:
    #        message.push_to_the_api()

    def send(self):
        for person in self.people.all():
            context = Context({'election':self.election, 'candidate': person, 'message': self})
            template_body = get_template('mails/nueva_pregunta_candidato_body.html')
            body = template_body.render(context)
            template_subject= get_template('mails/nueva_pregunta_candidato_subject.html')
            subject = template_subject.render(context).replace('\n', '').replace('\r', '')
            email = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL,
                             [person.email], [],
                             reply_to=[settings.DEFAULT_FROM_EMAIL], headers={})
            email.send()
            self.sent = True
            self.save()

    @classmethod
    def send_mails(cls):
        query = Q(accepted=True) & Q(sent=False)
        messages = Message.objects.filter(query)
        for message in messages:
            message.send()


    def reject_moderation(self):
        self.accepted = False
        self.save()


class Answer(models.Model):
    message = models.ForeignKey(Message, related_name='answers_')
    content = models.TextField()
    created = models.DateTimeField(editable=False, auto_now_add=True)
    person = models.ForeignKey(Candidate, related_name='answers_')
