# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase
from django.contrib.auth.models import User
from popular_proposal.models import ProposalTemporaryData
from popular_proposal.forms import ProposalForm
from django.core.urlresolvers import reverse
from django.core import mail
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.template.loader import get_template
from django.contrib.sites.models import Site


class TemporaryDataForPromise(ProposingCycleTestCaseBase):
    def setUp(self):
        super(TemporaryDataForPromise, self).setUp()

    def test_instanciate_one(self):
        temporary_data = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                              join_advocacy_url=u"http://whatsapp.com/mygroup",
                                                              data=self.data)
        self.assertTrue(temporary_data)
        self.assertTrue(temporary_data.join_advocacy_url)
        self.assertFalse(temporary_data.rejected)
        self.assertFalse(temporary_data.rejected_reason)

        self.assertIsNotNone(temporary_data.comments['title'])
        self.assertIsNotNone(temporary_data.comments['problem'])
        self.assertIsNotNone(temporary_data.comments['when'])
        self.assertIsNotNone(temporary_data.comments['causes'])
        self.assertIsNotNone(temporary_data.created)
        self.assertIsNotNone(temporary_data.updated)
        self.assertIsNotNone(temporary_data.overall_comments)
        self.assertEquals(temporary_data.status, ProposalTemporaryData.Statuses.InOurSide)
        self.assertIn(temporary_data, self.fiera.proposaltemporarydatas.all())
        self.assertEquals(temporary_data.get_title(), self.data['title'])
        self.assertEquals(str(temporary_data.get_title()), self.data['title'])

    def test_send_temporary_data_new_mail(self):
        temporary_data = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                              data=self.data)
        temporary_data.notify_new()
        self.assertEquals(len(mail.outbox), 1)
        the_mail = mail.outbox[0]
        self.assertTrue(the_mail)
        self.assertIn(self.fiera.email, the_mail.to)

    def test_needing_moderation_proposals(self):
        td_waiting_for_moderation = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                                         data=self.data)
        td_waiting_for_moderation2 = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                                          data=self.data)
        needs_citizen_action = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                                    status=ProposalTemporaryData.Statuses.InTheirSide,
                                                                    data=self.data)
        self.assertIn(td_waiting_for_moderation, ProposalTemporaryData.needing_moderation.all())
        self.assertIn(td_waiting_for_moderation2, ProposalTemporaryData.needing_moderation.all())
        self.assertNotIn(needs_citizen_action, ProposalTemporaryData.needing_moderation.all())

    def test_rejecting_a_proposal(self):
        temporary_data = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                              data=self.data)
        original_amount_of_mails = len(mail.outbox)
        temporary_data.reject('es muy mala la cosa')
        temporary_data = ProposalTemporaryData.objects.get(id=temporary_data.id)
        self.assertEquals(temporary_data.rejected_reason, 'es muy mala la cosa')
        self.assertEquals(temporary_data.status, ProposalTemporaryData.Statuses.Rejected)
        self.assertEquals(len(mail.outbox), original_amount_of_mails + 1)

        the_mail = mail.outbox[0]
        self.assertIn(self.fiera.email, the_mail.to)
        self.assertEquals(len(the_mail.to), 1)
        self.assertTrue(the_mail.body)
        self.assertTrue(the_mail.subject)
