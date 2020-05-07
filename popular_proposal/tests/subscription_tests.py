# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase as TestCase
from popular_proposal.models import (ProposalLike,
                                     Commitment,
                                     PopularProposal,
                                     )
from popular_proposal.subscriptions import (SubscriptionEventBase,
                                            EventDispatcher,
                                            ManyCitizensSupportingNotification,
                                            YouAreAHeroNotification,
                                            NewCommitmentNotificationToProposer,
                                            )

from django.core import mail
from elections.models import Candidate, Election
from backend_candidate.models import CandidacyContact, Candidacy
from django.test import override_settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils import timezone


class TestNewCandidateCommitment(SubscriptionEventBase):
    mail_template = 'new_commitment'

    def get_who(self):
        return self.proposal.likers.all()

    def get_mail_from(self, person):
        return person.email


class SubscriptionTestCaseBase(TestCase):
    def setUp(self):
        super(SubscriptionTestCaseBase, self).setUp()
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


class SubscriptionEventsTestCase(SubscriptionTestCaseBase):
    def setUp(self):
        super(SubscriptionEventsTestCase, self).setUp()

    def test_raises_not_implemented_error(self):
        class OnlyForThisTest(SubscriptionEventBase):
            pass
        bad_dispatcher = OnlyForThisTest(None)
        with self.assertRaises(NotImplementedError):
            bad_dispatcher.get_who()
        with self.assertRaises(NotImplementedError):
            bad_dispatcher.get_mail_from(None)

    def test_triggering_an_event(self):
        dispatcher = EventDispatcher()
        dispatcher.register('test-event', [TestNewCandidateCommitment, ])

        dispatcher.trigger('test-event', proposal=self.proposal)

        self.assertEquals(len(mail.outbox), 1)
        the_mail = mail.outbox[0]
        self.assertIn(self.fiera.email, the_mail.to)
        self.assertEquals(len(the_mail.to), 1)
        self.assertIn(self.proposal.title, the_mail.body)

    def test_letting_the_proposer_know_of_his_commitment(self):
        commitment = Commitment.objects.create(candidate=self.candidate,
                                               proposal=self.proposal,
                                               commited=True)
        previous_amount = len(mail.outbox)
        notifier = NewCommitmentNotificationToProposer(proposal=self.proposal,
                                                       commitment=commitment)
        notifier.notify()
        self.assertEquals(len(mail.outbox), previous_amount + 1)
        the_mail = mail.outbox[previous_amount]
        self.assertIn(self.proposal.proposer.email, the_mail.to)
        self.assertEquals(len(the_mail.to), 1)
        self.assertIn(self.proposal.title, the_mail.body)
        self.assertIn(self.candidate.name, the_mail.body)

    def test_letting_the_proposer_know_of_his_non_commitment(self):
        commitment = Commitment.objects.create(candidate=self.candidate,
                                               proposal=self.proposal,
                                               commited=False)
        previous_amount = len(mail.outbox)
        notifier = NewCommitmentNotificationToProposer(proposal=self.proposal,
                                                       commitment=commitment)
        notifier.notify()
        self.assertEquals(len(mail.outbox), previous_amount + 1)
        the_mail = mail.outbox[previous_amount]
        self.assertIn(self.proposal.proposer.email, the_mail.to)
        self.assertEquals(len(the_mail.to), 1)
        self.assertIn(self.proposal.title, the_mail.body)
        self.assertIn(self.candidate.name, the_mail.body)

    def test_notification_trigger_candidate_commit(self):
        original_amount_of_emails = len(mail.outbox)
        ProposalLike.objects.create(user=self.feli,
                                    proposal=self.proposal)
        Commitment.objects.create(candidate=self.candidate,
                                  proposal=self.proposal,
                                  commited=True)

        self.assertEquals(len(mail.outbox), original_amount_of_emails + 2)
        the_mail = mail.outbox[0]
        # Citizens are not notified if a candidate commits to a proposal
        # until further notice
        # self.assertIn(self.feli.email, the_mail.to)
        # self.assertEquals(len(the_mail.to), 1)
        # self.assertIn(self.proposal.title, the_mail.body)
        # self.assertIn(self.candidate.name, the_mail.body)

        # the_mail = mail.outbox[1]
        self.assertIn(self.fiera.email, the_mail.to)
        self.assertEquals(len(the_mail.to), 1)
        self.assertIn(self.proposal.title, the_mail.body)
        self.assertIn(self.candidate.name, the_mail.body)

    def test_there_are_two_different_emails_sent_if_a_candidate_has_not_commited(self):
        original_amount_of_emails = len(mail.outbox)
        ProposalLike.objects.create(user=self.feli,
                                    proposal=self.proposal)
        commitment = Commitment.objects.create(candidate=self.candidate,
                                               proposal=self.proposal,
                                               commited=True)

        self.assertEquals(len(mail.outbox), original_amount_of_emails + 2)
        the_mail = mail.outbox[original_amount_of_emails]
        commitment.delete()

        commitment = Commitment.objects.create(candidate=self.candidate,
                                               proposal=self.proposal,
                                               detail=u'Yo No me comprometo',
                                               commited=False)
        self.assertEquals(len(mail.outbox), original_amount_of_emails + 4)
        the_mail2 = mail.outbox[original_amount_of_emails + 1]
        self.assertNotEqual(the_mail.subject, the_mail2.subject)
        self.assertNotEqual(the_mail.body, the_mail2.body)
        self.assertTrue(the_mail2.body)
        self.assertTrue(the_mail2.subject)

    def test_letting_a_candidate_know_about_how_many_citizens_are_supporting_a_proposal(self):
        # According to setUp there should be at least one notification to
        # self.candidate

        Commitment.objects.create(candidate=self.candidate2,
                                  proposal=self.proposal,
                                  commited=True)
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
        # There is already a proposallike in the setUp
        # so with the previous one we make 2

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
        self.assertIn(the_mail.to[0], [self.contact.mail, self.contact2.mail])
        self.assertEquals(len(the_mail.to), 1)
        self.assertIn(self.proposal.title, the_mail.body)
        self.assertTrue(self.candidate.name in the_mail.body or self.candidate2.name in the_mail.body)
        self.assertIn(str(2), the_mail.body)
        # this should be the email to the other candidate
        the_mail = mail.outbox[2]
        self.assertIn(the_mail.to[0], [self.contact.mail, self.contact2.mail])
        self.assertEquals(len(the_mail.to), 1)
        self.assertIn(self.proposal.title, the_mail.body)
        self.assertTrue(self.candidate.name in the_mail.body or self.candidate2.name in the_mail.body)
        self.assertIn(str(2), the_mail.body)

    def test_proposal_notification_for_candidates(self):
        previous_amount = len(mail.outbox)
        proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                  area=self.arica,
                                                  data=self.data,
                                                  title=u'This is a title'
                                                  )
        proposal.notify_candidates_of_new()
        self.assertEquals(len(mail.outbox), previous_amount + 2)
        first_mail = mail.outbox[previous_amount]
        self.assertEquals(len(first_mail.to), 1)
        self.assertIn(first_mail.to[0], [self.contact.mail, self.contact2.mail])
        self.assertIn(proposal.title, first_mail.body)
        self.assertIn(self.arica.name, first_mail.body)
        self.assertIn(proposal.get_absolute_url(), first_mail.body)

        second_mail = mail.outbox[previous_amount]
        self.assertEquals(len(second_mail.to), 1)
        self.assertIn(second_mail.to[0], [self.contact.mail, self.contact2.mail])
        self.assertIn(proposal.title, second_mail.body)
        self.assertIn(self.arica.name, second_mail.body)
        self.assertIn(proposal.get_absolute_url(), first_mail.body)

    def test_new_proposal_notification_with_login_info(self):
        self.feli.last_login = None
        self.feli.save()
        CandidacyContact.objects.all().delete()
        candidacy = Candidacy.objects.create(user=self.feli,
                                             candidate=self.candidate
                                             )
        contact = CandidacyContact.objects.create(candidate=self.candidate,
                                                  mail='mail@perrito.cl',
                                                  initial_password='perrito',
                                                  candidacy=candidacy)
        previous_amount = len(mail.outbox)
        proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                  area=self.arica,
                                                  data=self.data,
                                                  title=u'This is a title'
                                                  )
        proposal.notify_candidates_of_new()
        first_mail = mail.outbox[previous_amount]
        contact = self.candidate.contacts.all().first()
        self.assertIn(self.feli.username, first_mail.body)
        self.assertIn(contact.initial_password, first_mail.body)

    def test_new_proposal_notification_with_media_naranja(self):
        self.feli.last_login = timezone.now()
        self.feli.save()
        self.candidate.taken_positions.all().delete()
        candidacy = Candidacy.objects.create(user=self.feli,
                                             candidate=self.candidate
                                             )
        CandidacyContact.objects.create(candidate=self.candidate,
                                        mail='mail@perrito.cl',
                                        initial_password='perrito',
                                        candidacy=candidacy)
        previous_amount = len(mail.outbox)
        proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                  area=self.arica,
                                                  data=self.data,
                                                  title=u'This is a title'
                                                  )
        proposal.notify_candidates_of_new()
        first_mail = mail.outbox[previous_amount]
        self.candidate.contacts.all().first()
        self.assertNotIn(self.feli.username, first_mail.body)

    @override_settings(NOTIFY_CANDIDATES_OF_NEW_PROPOSAL=False)
    def test_dont_notify_candidates_of_new_proposal(self):
        PopularProposal.objects.create(proposer=self.fiera,
                                       area=self.arica,
                                       data=self.data,
                                       title=u'This is a title'
                                       )

        self.assertEquals(len(mail.outbox), 0)


@override_settings(NOTIFY_CANDIDATES_WHEN_MANY_PROPOSALS_REACH_A_NUMBER=False)
class NotNotifyCandidatesUnlessToldSo(SubscriptionTestCaseBase):
    def setUp(self):
        super(NotNotifyCandidatesUnlessToldSo, self).setUp()

    @override_settings(WHEN_TO_NOTIFY=[2, 3])
    def test_not_notify_when_proposal_like(self):
        ProposalLike.objects.create(user=self.fiera,
                                    proposal=self.proposal)
        # There is already a proposallike in the setUp
        # so with the previous one we make 2

        self.assertEquals(len(mail.outbox), 1)
        # this should be the email to the proposer
        the_mail = mail.outbox[0]
        self.assertIn(self.proposal.proposer.email, the_mail.to)
        self.assertEquals(len(the_mail.to), 1)
        self.assertIn(self.proposal.title, the_mail.body)
        self.assertNotIn(self.candidate.name, the_mail.body)
        self.assertIn(str(2), the_mail.body)

    def test_dont_notify_candidates_of_new_proposal(self):
        PopularProposal.objects.create(proposer=self.fiera,
                                       area=self.arica,
                                       data=self.data,
                                       title=u'This is a title'
                                       )

        self.assertEquals(len(mail.outbox), 0)


class HomeWithProposalsViewTestCase(TestCase):
    def setUp(self):
        super(HomeWithProposalsViewTestCase, self).setUp()
        amount_of_likers = [2, 4, 1, 3]
        for i in range(1, 5):
            title = 'this is a title' + str(i)
            proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                      area=self.arica,
                                                      data=self.data,
                                                      title=title
                                                      )

            for j in range(0, amount_of_likers[i - 1]):
                password = User.objects.make_random_password()
                username = 'user_' + str(j) + '_' + str(i)
                user = User.objects.create_user(username=username, password=password)
                ProposalLike.objects.create(user=user,
                                            proposal=proposal)
            setattr(self, 'proposal' + str(i), proposal)

    def test_manager_adds_extra_attr(self):
        ps = PopularProposal.ordered.all()
        p = ps.get(id=self.proposal2.id)
        self.assertTrue(hasattr(p, 'num_likers'))
        self.assertEquals(p.num_likers, 4)

    def test_manager_order_by_likes(self):
        ps = PopularProposal.ordered.by_likers()
        # this proposal has 4 likes
        self.assertEquals(ps.all()[0], self.proposal2)
        # this proposal has 4 likes
        self.assertEquals(ps.all()[1], self.proposal4)
        # this proposal has 4 likes
        self.assertEquals(ps.all()[2], self.proposal1)
        # this proposal has 4 likes
        self.assertEquals(ps.all()[3], self.proposal3)
