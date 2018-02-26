# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase as TestCase
from popular_proposal.models import (ProposalLike,
                                     Commitment,
                                     PopularProposal,
                                     )
from popular_proposal.subscriptions import (SubscriptionEventBase,
                                            EventDispatcher,
                                            YouAreAHeroNotification,
                                            NewCommitmentNotificationToProposer,
                                            )

from django.core import mail

from django.test import override_settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from popular_proposal import get_authority_model


authority_model = get_authority_model()


class TestNewAuthorityCommitment(SubscriptionEventBase):
    mail_template = 'new_commitment'

    def get_who(self):
        return self.proposal.likers.all()

    def get_mail_from(self, person):
        return person.email


class SubscriptionTestCaseBase(TestCase):
    def setUp(self):
        super(SubscriptionTestCaseBase, self).setUp()
        self.proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                       data=self.data,
                                                       title=u'This is a title'
                                                       )
        self.like = ProposalLike.objects.create(user=self.fiera,
                                                proposal=self.proposal)
        


class SubscriptionEventsTestCase(SubscriptionTestCaseBase):
    def setUp(self):
        super(SubscriptionEventsTestCase, self).setUp()
        self.authority = authority_model.objects.get(id=1)

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
        dispatcher.register('test-event', [TestNewAuthorityCommitment, ])

        dispatcher.trigger('test-event', proposal=self.proposal)

        self.assertEquals(len(mail.outbox), 1)
        the_mail = mail.outbox[0]
        self.assertIn(self.fiera.email, the_mail.to)
        self.assertEquals(len(the_mail.to), 1)
        self.assertIn(self.proposal.title, the_mail.body)

    def test_letting_the_proposer_know_of_his_commitment(self):
        commitment = Commitment.objects.create(authority=self.authority,
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
        self.assertIn(self.authority.name, the_mail.body)

    def test_letting_the_proposer_know_of_his_non_commitment(self):
        commitment = Commitment.objects.create(authority=self.authority,
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
        self.assertIn(self.authority.name, the_mail.body)

    def test_notification_trigger_commit(self):
        original_amount_of_emails = len(mail.outbox)
        ProposalLike.objects.create(user=self.feli,
                                    proposal=self.proposal)
        Commitment.objects.create(authority=self.authority,
                                  proposal=self.proposal,
                                  commited=True)

        self.assertEquals(len(mail.outbox), original_amount_of_emails + 2)
        the_mail = mail.outbox[0]
        # Citizens are not notified if an authority commits to a proposal
        # until further notice
        # self.assertIn(self.feli.email, the_mail.to)
        # self.assertEquals(len(the_mail.to), 1)
        # self.assertIn(self.proposal.title, the_mail.body)
        # self.assertIn(self.authority.name, the_mail.body)

        # the_mail = mail.outbox[1]
        self.assertIn(self.fiera.email, the_mail.to)
        self.assertEquals(len(the_mail.to), 1)
        self.assertIn(self.proposal.title, the_mail.body)
        self.assertIn(self.authority.name, the_mail.body)

    def test_there_are_two_different_emails_sent_if_an_authority_has_not_commited(self):
        original_amount_of_emails = len(mail.outbox)
        ProposalLike.objects.create(user=self.feli,
                                    proposal=self.proposal)
        commitment = Commitment.objects.create(authority=self.authority,
                                               proposal=self.proposal,
                                               commited=True)

        self.assertEquals(len(mail.outbox), original_amount_of_emails + 2)
        the_mail = mail.outbox[original_amount_of_emails]
        commitment.delete()

        commitment = Commitment.objects.create(authority=self.authority,
                                               proposal=self.proposal,
                                               detail=u'Yo No me comprometo',
                                               commited=False)
        self.assertEquals(len(mail.outbox), original_amount_of_emails + 4)
        the_mail2 = mail.outbox[original_amount_of_emails + 1]
        self.assertNotEqual(the_mail.subject, the_mail2.subject)
        self.assertNotEqual(the_mail.body, the_mail2.body)
        self.assertTrue(the_mail2.body)
        self.assertTrue(the_mail2.subject)

    def test_letting_the_proposer_know_that_there_are_many_proposers(self):
        notifier = YouAreAHeroNotification(proposal=self.proposal,
                                           number=4)
        notifier.notify()
        self.assertEquals(len(mail.outbox), 1)
        the_mail = mail.outbox[0]
        self.assertIn(self.proposal.proposer.email, the_mail.to)
        self.assertEquals(len(the_mail.to), 1)
        self.assertIn(self.proposal.title, the_mail.body)
        self.assertNotIn(self.authority.name, the_mail.body)
        self.assertIn(str(notifier.number), the_mail.body)


class HomeWithProposalsViewTestCase(TestCase):
    def setUp(self):
        super(HomeWithProposalsViewTestCase, self).setUp()
        amount_of_likers = [2, 4, 1, 3]
        for i in range(1, 5):
            title = 'this is a title' + str(i)
            proposal = PopularProposal.objects.create(proposer=self.fiera,
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

    def test_get_home_with_the_proposals(self):
        url = reverse('home')
        response = self.client.get(url)
        ps = response.context['proposals_with_likers']
        # this proposal has 4 likes
        self.assertEquals(ps.all()[0], self.proposal2)
        # this proposal has 4 likes
        self.assertEquals(ps.all()[1], self.proposal4)
        # this proposal has 4 likes
        self.assertEquals(ps.all()[2], self.proposal1)
