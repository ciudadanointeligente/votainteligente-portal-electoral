from django.conf import settings
from popular_proposal.models import Commitment, ProposalLike, PopularProposal
from backend_candidate.models import CandidacyContact
from popular_proposal.subscriptions import NumericNotificationBase
from elections.models import Candidate



class ManyCitizensSupportingNotification(NumericNotificationBase):
    mail_template = 'many_citizens_supporting'

    def get_who(self):
        if not settings.NOTIFY_CANDIDATES:
            return []
        commitments = Commitment.objects.filter(proposal=self.proposal)
        candidates_pks = []
        for commitment in commitments:
            candidates_pks.append(commitment.authority.id)

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