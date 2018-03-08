# coding=utf-8
from proposals_for_votainteligente.tests import VIProposingCycleTestCaseBase as TestCase
from popular_proposal.models import (ProposalLike,
                                     Commitment,
                                     PopularProposal,
                                     )
from proposals_for_votainteligente.subscriptions import (ManyCitizensSupportingNotification
                                            )
from popular_proposal.tests.subscription_tests import SubscriptionTestCaseBase
from elections.models import Candidate, Election
from elections.models import Area, Candidate
from backend_candidate.models import CandidacyContact, Candidacy
from django.test import override_settings
from django.utils import timezone

from django.core import mail


class NewSubscriptionTestCase(SubscriptionTestCaseBase):
    def setUp(self):
        super(NewSubscriptionTestCase, self).setUp()
        self.arica = Area.objects.get(id='arica-15101')
        self.proposal.area = self.arica
        self.proposal.save()
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


class SubscriptionEventsTestCase(NewSubscriptionTestCase):
    def setUp(self):
        super(SubscriptionEventsTestCase, self).setUp()

    def test_letting_a_candidate_know_about_how_many_citizens_are_supporting_a_proposal(self):
        # According to setUp there should be at least one notification to
        # self.candidate

        Commitment.objects.create(authority=self.candidate2,
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




@override_settings(NOTIFY_CANDIDATES=False,
                   NUMERICAL_NOTIFICATION_CLASSES = [ 'popular_proposal.subscriptions.YouAreAHeroNotification',
                                  'proposals_for_votainteligente.subscriptions.ManyCitizensSupportingNotification'
                                  ])
class NotNotifyCandidatesUnlessToldSo(NewSubscriptionTestCase):
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
                                       data=self.data,
                                       title=u'This is a title'
                                       )

        self.assertEquals(len(mail.outbox), 0)


class SubscriptionEventsTestCase(NewSubscriptionTestCase):
    def setUp(self):
        super(SubscriptionEventsTestCase, self).setUp()

    @override_settings(WHEN_TO_NOTIFY=[2, 3],
                       NUMERICAL_NOTIFICATION_CLASSES = [ 'popular_proposal.subscriptions.YouAreAHeroNotification',
                                      'proposals_for_votainteligente.subscriptions.ManyCitizensSupportingNotification'
                                      ])
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
        proposal.notify_authorities_of_new()
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
        proposal.notify_authorities_of_new()
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
        proposal.notify_authorities_of_new()
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