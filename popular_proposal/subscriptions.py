from collections import OrderedDict
from popular_proposal import send_mail
from popular_proposal.models import Commitment, ProposalLike, PopularProposal
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.conf import settings


class SubscriptionEventBase(object):
    def get_who(self):
        raise NotImplementedError

    def get_mail_from(self, person):
        raise NotImplementedError

    def __init__(self, proposal, *args, **kwargs):
        self.proposal = proposal

    def get_context(self, person):
        return {'proposal': self.proposal,
                'person': person}

    def get_template(self):
        return self.mail_template

    def notify(self):
        for person in self.get_who():
            email = self.get_mail_from(person)
            context = self.get_context(person=person)
            template = self.get_template()
            send_mail(context, template,
                      to=[email])


class NewCommitmentNotificationToProposer(SubscriptionEventBase):
    mail_template = 'genia_lograste_compromiso'

    def __init__(self, *args, **kwargs):
        super(NewCommitmentNotificationToProposer, self).__init__(*args, **kwargs)
        self.commitment = kwargs.pop('commitment')

    def get_who(self):
        return [self.proposal.proposer, ]

    def get_mail_from(self, person):
        return person.email

    def get_template(self):
        if self.commitment.commited:
            return 'genia_lograste_compromiso'
        else:
            return 'genia_lo_sentimos'

    def get_context(self, **kwargs):
        context = super(NewCommitmentNotificationToProposer, self).get_context(**kwargs)
        context['commitment'] = self.commitment
        return context


class NumericNotificationBase(SubscriptionEventBase):
    def __init__(self, *args, **kwargs):
        super(NumericNotificationBase, self).__init__(*args, **kwargs)
        self.number = kwargs.pop('number')

    def get_context(self, **kwargs):
        context = super(NumericNotificationBase, self).get_context(**kwargs)
        context['number'] = self.number
        return context


class YouAreAHeroNotification(NumericNotificationBase):
    mail_template = 'sos_una_grande'

    def get_who(self):
        return [self.proposal.proposer, ]

    def get_mail_from(self, proposer):
        return proposer.email


class EventDispatcher(object):
    events = OrderedDict({'new-commitment': [##  NewCommitmentNotification,
                                             NewCommitmentNotificationToProposer]})

    def register(self, event, event_class):
        self.events[event] = event_class

    def trigger(self, event, proposal, kwargs={}):
        for event_nofifier_class in self.events[event]:
            event_nofifier = event_nofifier_class(proposal, **kwargs)
            event_nofifier.notify()


def notification_trigger(event, **kwargs):
    dispatcher = EventDispatcher()
    proposal = kwargs.pop('proposal')
    dispatcher.trigger(event, proposal, kwargs)
