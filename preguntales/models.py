# coding=utf-8
from django.db import models
from elections.models import Election, Candidate
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q, Count
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from autoslug import AutoSlugField
from django.conf import settings
from uuid import uuid4
from django.utils import timezone
from popolo.models import Person
from votainteligente.send_mails import send_mail


class MessageManagerBase(models.Manager):
    def needing_moderation_messages(self):
        qs = self.filter(status__accepted__isnull=True)
        return qs


class MessageManager(MessageManagerBase):
    def get_queryset(self):
        queryset = super(MessageManager, self).get_queryset().annotate(num_answers=Count('answers'))
        return queryset.order_by('-num_answers', '-status__accepted', '-created')


def uuid_with_no_dashes():
    return uuid4().hex


@python_2_unicode_compatible
class Message(models.Model):
    author_name = models.CharField(max_length=256, default='')
    author_email = models.EmailField(max_length=512, default='')
    content = models.TextField(default='')
    people = models.ManyToManyField(Candidate)
    subject = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from='subject', unique=True, null=False)

    election = models.ForeignKey(Election, related_name='messages', default=None)
    created = models.DateTimeField(auto_now_add=True)

    objects = MessageManagerBase()
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

    def __init__(self, *args, **kwargs):
        self.possible_status = {}
        self.possible_status['accepted'] = kwargs.pop('accepted', None)
        self.possible_status['sent'] = kwargs.pop('sent', None)
        self.possible_status['confirmed'] = kwargs.pop('confirmed', None)
        super(Message, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        creating = False
        if self.pk is None:
            creating = True
        super(Message, self).save(*args, **kwargs)
        if creating:
            status = MessageStatus.objects.create(message=self)
        if self.possible_status['accepted'] is not None:
            self.accepted = self.possible_status['accepted']
        if self.possible_status['sent'] is not None:
            self.sent = self.possible_status['sent']
        if self.possible_status['accepted'] is not None:
            self.confirmed = self.possible_status['confirmed']

    def create_confirmation(self):
        confirmation = MessageConfirmation.objects.create(message=self)
        site = Site.objects.get_current()
        context = {'election':self.election,
                   'message': self,
                   'site': site}
        send_mail(context, 'confirmation', to=[self.author_email], from_email=settings.NO_REPLY_MAIL)

    def confirm(self):
        self.confirmed = True
        self.confirmation.when_confirmed = timezone.now()
        self.confirmation.save()

    def get_absolute_url(self):
        election = self.election
        path = reverse('message_detail', kwargs={'election_slug': election.slug, 'pk': self.id})
        site = Site.objects.get_current()
        return "http://%s%s" % (site.domain, path)

    def get_sent(self):
        return self.status.sent

    def set_sent(self, sent):
        self.status.sent = sent
        self.status.save()

    sent = property(get_sent, set_sent)

    def get_accepted(self):
        return self.status.accepted

    def set_accepted(self, accepted):
        self.status.accepted = accepted
        self.status.save()

    accepted = property(get_accepted, set_accepted)

    def get_confirmed(self):
        return self.status.confirmed

    def set_confirmed(self, confirmed):
        self.status.confirmed = confirmed
        self.status.save()

    confirmed = property(get_confirmed, set_confirmed)

    def send(self):
        for person in self.people.all():
            outbound_message = OutboundMessage.objects.create(message=self, person=person)
            reply_to = '%(localpart)s+%(key)s@%(domain)s' % {'localpart': settings.EMAIL_LOCALPART,
                                                             'key': outbound_message.key,
                                                             'domain': settings.EMAIL_DOMAIN}
            site = Site.objects.get_current()
            context = {'election':self.election,
                       'candidate': person,
                       'message': self,
                       'site': site}
            send_mail(context, 'nueva_pregunta_candidato', to=[person.email], \
                      reply_to=reply_to)
        self.status.sent = True
        self.status.save()

    @classmethod
    def send_mails(cls):
        query = Q(status__accepted=True) & Q(status__sent=False)
        messages = Message.objects.filter(query)
        for message in messages:
            message.send()


    def reject_moderation(self):
        self.accepted = False
        self.save()

class Answer(models.Model):
    message = models.ForeignKey(Message, related_name='answers')
    content = models.TextField()
    created = models.DateTimeField(editable=False, auto_now_add=True)
    person = models.ForeignKey(Candidate, related_name='answers')

class Attachment(models.Model):
    answer = models.ForeignKey(Answer, related_name='attachments')
    content = models.FileField(upload_to="attachments/%Y/%m/%d")
    name = models.CharField(max_length=255)

class OutboundMessage(models.Model):
    message = models.ForeignKey(Message, related_name='outbound_identifiers')
    person = models.ForeignKey(Person)
    key = models.CharField(max_length=255, default=uuid_with_no_dashes)

class MessageStatus(models.Model):
    message = models.OneToOneField(Message, related_name='status')
    accepted = models.NullBooleanField(default=None)
    sent = models.BooleanField(default=False)
    confirmed = models.NullBooleanField(default=None)


class MessageConfirmation(models.Model):
    message = models.OneToOneField(Message, related_name='confirmation')
    key = models.CharField(max_length=255, default=uuid_with_no_dashes)
    when_confirmed = models.DateTimeField(default=None, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('confirmation', kwargs={'key': self.key})
