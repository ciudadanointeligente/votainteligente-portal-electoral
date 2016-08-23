# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase as TestCase
from popular_proposal.models import (ProposalLike,
                                     Commitment,
                                     PopularProposal,
                                     )
from popular_proposal.subscriptions import (SubscriptionEventBase,
                                            EventDispatcher,
                                            notification_trigger,
                                            NewCommitmentNotification
                                            )
from django.core import mail
from elections.models import Candidate


class TestNewCandidateCommitment(SubscriptionEventBase):
    mail_template = 'new_commitment'

    def get_who(self):
        return self.proposal.likers.all()

    def get_mail_from(self, person):
        return person.email


class SubscriptionEventsTestCase(TestCase):
    def setUp(self):
        super(SubscriptionEventsTestCase, self).setUp()
        self.proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                       area=self.arica,
                                                       data=self.data,
                                                       title=u'This is a title'
                                                       )
        self.like = ProposalLike.objects.create(user=self.fiera,
                                                proposal=self.proposal)

        self.candidate = Candidate.objects.get(id=1)

    def test_triggering_an_event(self):
        dispatcher = EventDispatcher()
        dispatcher.register('test-event', TestNewCandidateCommitment)

        dispatcher.trigger('test-event', proposal=self.proposal)

        self.assertEquals(len(mail.outbox), 1)
        the_mail = mail.outbox[0]
        self.assertIn(self.fiera.email, the_mail.to)
        self.assertEquals(len(the_mail.to), 1)
        self.assertIn(self.proposal.title, the_mail.body)

    def test_letting_know_the_citizens_that_a_candidate_has_commited_to_a_proposal(self):
        commitment = Commitment.objects.create(candidate=self.candidate,
                                               proposal=self.proposal,
                                               detail=u'Yo me comprometo')

        notifier = NewCommitmentNotification(proposal=self.proposal,
                                             commitment=commitment)
        notifier.notify()
        self.assertEquals(len(mail.outbox), 1)
        the_mail = mail.outbox[0]
        self.assertIn(self.fiera.email, the_mail.to)
        self.assertEquals(len(the_mail.to), 1)
        self.assertIn(self.proposal.title, the_mail.body)
        self.assertIn(self.candidate.name, the_mail.body)
        self.assertIn(commitment.detail, the_mail.body)

    def test_notification_trigger_candidate_commit(self):
        commitment = Commitment.objects.create(candidate=self.candidate,
                                               proposal=self.proposal,
                                               detail=u'Yo me comprometo')
        notification_trigger('new-commitment', proposal=self.proposal, commitment=commitment)
        self.assertEquals(len(mail.outbox), 1)
        the_mail = mail.outbox[0]
        self.assertIn(self.fiera.email, the_mail.to)
        self.assertEquals(len(the_mail.to), 1)
        self.assertIn(self.proposal.title, the_mail.body)
        self.assertIn(self.candidate.name, the_mail.body)
        self.assertIn(commitment.detail, the_mail.body)
