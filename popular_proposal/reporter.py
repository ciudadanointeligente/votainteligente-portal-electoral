from votai_utils.send_mails import send_mail
from django.conf import settings
from popular_proposal.models import PopularProposal
import datetime
from django.utils import timezone


class PeriodicReporter(object):
    mail_template = 'periodic_report'
    def __init__(self, user, days=settings.HOW_OFTEN_PROPOSAL_REPORTS_ARE_SENT):
        self.user = user
        self.days = days

    def get_proposals(self):
        return self.user.proposals.all()

    def get_proposals_dict(self):
        proposals_dict = []
        for proposal in self.get_proposals():
            proposal_dict = {
                'proposal': proposal,
                'analytics': proposal.get_analytics(days=self.days)
            }
            proposals_dict.append(proposal_dict)
        return proposals_dict

    def get_new_proposals(self):
        classifications = [p.clasification for p in self.get_proposals()]
        since_when = timezone.now() - datetime.timedelta(days=self.days)
        proposals = PopularProposal.objects.exclude(proposer=self.user)
        proposals = proposals.exclude(likers=self.user)
        proposals = proposals.filter(clasification__in=classifications)
        proposals = proposals.filter(created__gte=since_when)
        return proposals

    def get_mail_context(self):
        context = {'user': self.user}

        context['proposals'] = self.get_proposals_dict()
        if self.user.profile.is_organization:
            context['new_proposals'] = self.get_new_proposals()
            print(context['new_proposals'])
        return context

    def send_mail(self):
        context = self.get_mail_context()
        if context['proposals']:
            send_mail(context, self.mail_template,
                      to=[self.user.email])
