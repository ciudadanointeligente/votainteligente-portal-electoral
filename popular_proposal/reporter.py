from votai_utils.send_mails import send_mail
from django.conf import settings


class PeriodicReporter(object):
    mail_template = 'periodic_report'
    def __init__(self, user, days=settings.HOW_OFTEN_PROPOSAL_REPORTS_ARE_SENT):
        self.user = user
        self.days = days

    def get_proposals(self):
        return self.user.proposals.all()

    def get_mail_context(self):
        context = {'user': self.user}
        proposals_dict = []
        for proposal in self.get_proposals():
            proposal_dict = {
                'proposal': proposal,
                'analytics': proposal.get_analytics(days=self.days)
            }
            proposals_dict.append(proposal_dict)
        context['proposals'] = proposals_dict
        return context

    def send_mail(self):
        context = self.get_mail_context()
        if context['proposals']:
            send_mail(context, self.mail_template,
                      to=[self.user.email])
