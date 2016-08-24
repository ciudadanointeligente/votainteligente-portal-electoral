from collections import OrderedDict
from votainteligente.send_mails import send_mail
from elections.models import Candidate
from backend_candidate.models import CandidacyContact
from popular_proposal.models import Commitment


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

    def notify(self):
        for person in self.get_who():
            email = self.get_mail_from(person)
            context = self.get_context(person=person)
            send_mail(context, self.mail_template,
                      to=[email])


class NewCommitmentNotification(SubscriptionEventBase):
    mail_template = 'new_commitment'

    def __init__(self, *args, **kwargs):
        super(NewCommitmentNotification, self).__init__(*args, **kwargs)
        self.commitment = kwargs.pop('commitment')

    def get_who(self):
        return self.proposal.likers.all()

    def get_mail_from(self, person):
        return person.email

    def get_context(self, **kwargs):
        context = super(NewCommitmentNotification, self).get_context(**kwargs)
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


class ManyCitizensSupportingNotification(NumericNotificationBase):
    mail_template = 'many_citizens_supporting'

    def get_who(self):
        commitments = Commitment.objects.filter(proposal=self.proposal)
        candidates_pks = []
        for commitment in commitments:
            candidates_pks.append(commitment.candidate.id)

        candidates = Candidate.objects.filter(elections__area=self.proposal.area).exclude(id__in=candidates_pks)
        contacts = CandidacyContact.objects.filter(candidate__in=candidates)
        return contacts

    def get_mail_from(self, contact):
        return contact.mail

    def get_context(self, **kwargs):
        context = super(ManyCitizensSupportingNotification, self).get_context(**kwargs)
        contact = kwargs.pop('person')
        context['contact'] = contact
        return context


class YouAreAHeroNotification(NumericNotificationBase):
    mail_template = 'sos_una_grande'

    def get_who(self):
        return [self.proposal.proposer, ]

    def get_mail_from(self, proposer):
        return proposer.email


class EventDispatcher(object):
    events = OrderedDict({'new-commitment': NewCommitmentNotification})

    def register(self, event, event_class):
        self.events[event] = event_class

    def trigger(self, event, proposal, kwargs={}):
        event_nofifier = self.events[event](proposal, **kwargs)
        event_nofifier.notify()


def notification_trigger(event, **kwargs):
    dispatcher = EventDispatcher()
    proposal = kwargs.pop('proposal')
    dispatcher.trigger(event, proposal, kwargs)
