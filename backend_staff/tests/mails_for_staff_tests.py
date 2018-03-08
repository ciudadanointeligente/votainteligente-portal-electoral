# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase as TestCase
from votai_utils.send_mails import send_mails_to_staff
from django.contrib.auth.models import User
from popular_proposal.models import ProposalTemporaryData, PopularProposal
from django.core import mail


class MailsForStaffTestCase(TestCase):
    def setUp(self):
        super(MailsForStaffTestCase, self).setUp()
        self.staff1 = User.objects.create_superuser(username='staff1',
                                                    password='perrito',
                                                    email='staff1@staffs.cl')
        self.staff2 = User.objects.create_superuser(username='staff2',
                                                    password='perrito',
                                                    email='staff2@staffs.cl')
        self.temporary_data = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                                   area=self.arica,
                                                                   data=self.data)
        self.proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                       area=self.arica,
                                                       data=self.data,
                                                       title=u'This is a title',
                                                       clasification=u'education'
                                                       )

    def test_send_mails_to_staff_when_new_comments(self):
        context = {
            'temporary_data': self.temporary_data,
        }
        send_mails_to_staff(context, 'notify_staff_new_proposal_update')
        self.assertEquals(len(mail.outbox), 1)
        the_mail = mail.outbox[0]
        self.assertIn(self.staff1.email, the_mail.to)
        self.assertIn(self.staff2.email, the_mail.to)
        self.assertIn(str(self.temporary_data.id), the_mail.body)
        self.assertIn(self.temporary_data.get_title(), the_mail.body)

    def test_send_mails_to_staff_when_new_proposal(self):
        context = {
            'temporary_data': self.temporary_data,
        }
        send_mails_to_staff(context, 'notify_staff_new_proposal')
        self.assertEquals(len(mail.outbox), 1)
        the_mail = mail.outbox[0]
        self.assertIn(self.staff1.email, the_mail.to)
        self.assertIn(self.staff2.email, the_mail.to)
        self.assertIn(self.temporary_data.get_title(), the_mail.body)
        self.assertIn(self.temporary_data.area.name, the_mail.subject)
