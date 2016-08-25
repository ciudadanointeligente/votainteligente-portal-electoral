# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase as TestCase
from popular_proposal.models import (ProposalLike,
                                     Commitment,
                                     PopularProposal,
                                     )
from popular_proposal.subscriptions import (SubscriptionEventBase,
                                            EventDispatcher,
                                            notification_trigger,
                                            NewCommitmentNotification,
                                            ManyCitizensSupportingNotification,
                                            YouAreAHeroNotification,
                                            )

from django.core import mail
from elections.models import Candidate, Election
from backend_candidate.models import CandidacyContact
from django.test import override_settings


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
        self.election = Election.objects.create(name=u'Elección para Arica')
        self.election.area = self.arica
        self.election.save()
        self.candidate = Candidate.objects.get(id=1)
        self.contact = CandidacyContact.objects.create(candidate=self.candidate,
                                                       mail='mail@perrito.cl')
        self.election.candidates.add(self.candidate)

        self.candidate2 = Candidate.objects.get(id=2)
        self.contact2 = CandidacyContact.objects.create(candidate=self.candidate2,
                                                        mail='mail@gatito.cl')
        self.election.candidates.add(self.candidate2)

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
        previous_amount = len(mail.outbox)
        notifier = NewCommitmentNotification(proposal=self.proposal,
                                             commitment=commitment)
        notifier.notify()
        self.assertEquals(len(mail.outbox), previous_amount + 1)
        the_mail = mail.outbox[previous_amount]
        self.assertIn(self.fiera.email, the_mail.to)
        self.assertEquals(len(the_mail.to), 1)
        self.assertIn(self.proposal.title, the_mail.body)
        self.assertIn(self.candidate.name, the_mail.body)
        self.assertIn(commitment.detail, the_mail.body)

    def test_notification_trigger_candidate_commit(self):
        commitment = Commitment.objects.create(candidate=self.candidate,
                                               proposal=self.proposal,
                                               detail=u'Yo me comprometo')

        self.assertEquals(len(mail.outbox), 1)
        the_mail = mail.outbox[0]
        self.assertIn(self.fiera.email, the_mail.to)
        self.assertEquals(len(the_mail.to), 1)
        self.assertIn(self.proposal.title, the_mail.body)
        self.assertIn(self.candidate.name, the_mail.body)
        self.assertIn(commitment.detail, the_mail.body)

    def test_letting_a_candidate_know_about_how_many_citizens_are_supporting_a_proposal(self):
        # According to setUp there should be at least one notification to
        # self.candidate

        Commitment.objects.create(candidate=self.candidate2,
                                  proposal=self.proposal,
                                  detail=u'Yo me comprometo')
        previous_amount = len(mail.outbox)
        # We should not notify candidates that have already been commited
        notifier = ManyCitizensSupportingNotification(proposal=self.proposal,
                                                      number=4)
        notifier.notify()
        self.assertEquals(len(mail.outbox), previous_amount + 1)
        the_mail = mail.outbox[previous_amount]
        self.assertIn(self.contact.mail, the_mail.to)
        self.assertEquals(len(the_mail.to), 1)
        self.assertIn(self.proposal.title, the_mail.body)
        self.assertIn(self.candidate.name, the_mail.body)
        self.assertIn(str(notifier.number), the_mail.body)

    def test_letting_the_proposer_know_that_there_are_many_proposers(self):
        notifier = YouAreAHeroNotification(proposal=self.proposal,
                                           number=4)
        notifier.notify()
        self.assertEquals(len(mail.outbox), 1)
        the_mail = mail.outbox[0]
        self.assertIn(self.proposal.proposer.email, the_mail.to)
        self.assertEquals(len(the_mail.to), 1)
        self.assertIn(self.proposal.title, the_mail.body)
        self.assertNotIn(self.candidate.name, the_mail.body)
        self.assertIn(str(notifier.number), the_mail.body)

    @override_settings(WHEN_TO_NOTIFY=[2, 3])
    def test_like_a_proposal_signal(self):
        ProposalLike.objects.create(user=self.fiera,
                                    proposal=self.proposal)
        ProposalLike.objects.create(user=self.feli,
                                    proposal=self.proposal)

        self.assertEquals(len(mail.outbox), 3)
        # this should be the email to the proposer
        the_mail = mail.outbox[0]
        self.assertIn(self.proposal.proposer.email, the_mail.to)
        self.assertEquals(len(the_mail.to), 1)
        self.assertIn(self.proposal.title, the_mail.body)
        self.assertNotIn(self.candidate.name, the_mail.body)
        self.assertIn(str(2), the_mail.body)
        # this should be the email to the candidate
        the_mail = mail.outbox[1]
        self.assertIn(self.contact.mail, the_mail.to)
        self.assertEquals(len(the_mail.to), 1)
        self.assertIn(self.proposal.title, the_mail.body)
        self.assertIn(self.candidate.name, the_mail.body)
        self.assertIn(str(2), the_mail.body)
        # this should be the email to the other candidate
        the_mail = mail.outbox[2]
        self.assertIn(self.contact2.mail, the_mail.to)
        self.assertEquals(len(the_mail.to), 1)
        self.assertIn(self.proposal.title, the_mail.body)
        self.assertIn(self.candidate2.name, the_mail.body)
        self.assertIn(str(2), the_mail.body)