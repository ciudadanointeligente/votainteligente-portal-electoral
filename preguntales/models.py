# coding=utf-8
from django.db import models
from writeit.models import Message as WriteItMessage
from elections.models import Election
from elections.models import Candidate
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from elections import get_writeit_instance
from django.db.models import Q, Count
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site


class MessageManager(models.Manager):
    def get_queryset(self):
        queryset = super(MessageManager, self).get_queryset().annotate(num_answers=Count('answers_'))
        return queryset.order_by('-num_answers', '-moderated', '-created')


@python_2_unicode_compatible
class Message(WriteItMessage):
    message = models.OneToOneField(WriteItMessage, related_name="%(app_label)s_%(class)s_related")
    moderated = models.NullBooleanField(default=None)
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
        self.moderated = True
        self.save()

    def save(self, *args, **kwargs):

        if self.api_instance_id is None or self.writeitinstance_id is None:
            writeit_instance = get_writeit_instance()
            self.api_instance = writeit_instance.api_instance
            self.writeitinstance = writeit_instance
        super(Message, self).save(*args, **kwargs)

    def get_absolute_url(self):
        election = self.election
        path = reverse('message_detail', kwargs={'election_slug': election.slug, 'pk': self.id})
        site = Site.objects.get_current()
        return "http://%s%s" % (site.domain, path)

    @classmethod
    def push_moderated_messages_to_writeit(cls):
        query = Q(moderated=True) & Q(remote_id=None)
        messages = Message.objects.filter(query)
        for message in messages:
            message.push_to_the_api()

    def reject_moderation(self):
        self.moderated = True
        self.save()


class Answer(models.Model):
    message = models.ForeignKey(Message, related_name='answers_')
    content = models.TextField()
    created = models.DateTimeField(editable=False, auto_now_add=True)
    person = models.ForeignKey(Candidate, related_name='answers_')
