# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase
from hitcount.models import HitCount, Hit
from django.contrib.auth.models import User
from popular_proposal.models import (PopularProposal,
                                     Commitment,
                                     ProposalLike)
from elections.models import Candidate
import datetime
from django.utils import timezone
from django.core import mail
from popular_proposal.reporter import PeriodicReporter
from popular_proposal.tasks import (report_sender_task)
from constance.test import override_config


TODAY = timezone.now()
YESTERDAY = timezone.now() - datetime.timedelta(days=1)
TWO_DAYS_AGO = timezone.now() - datetime.timedelta(days=2)


class PeriodicProposalTestCaseMixin(object):
    def set_proposals_and_data(self):
        self.popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                               area=self.arica,
                                                               data=self.data,
                                                               title=u'This is a title',
                                                               clasification=u'education'
                                                              )
        # Has one visitor
        self.client.get(self.popular_proposal.get_absolute_url())
        self.hit_count = HitCount.objects.get_for_object(self.popular_proposal)
        # Has one support
        lovely_user = User.objects.create_user(username="lovely")
        self.like = ProposalLike.objects.create(user=lovely_user,
                                                proposal=self.popular_proposal)
        # Has one commitment
        self.candidate = Candidate.objects.get(id=1)
        self.commitment = Commitment.objects.create(candidate=self.candidate,
                                                    proposal=self.popular_proposal,
                                                    detail=u'Yo me comprometo',
                                                    commited=True)
        hit = Hit.objects.get(hitcount=self.hit_count)
        hit.created = TWO_DAYS_AGO
        hit.save()
        self.commitment.created = TWO_DAYS_AGO
        self.commitment.save()
        self.like.created  = TWO_DAYS_AGO
        self.like.save()


class PopularProposalAnalyticsTestCase(ProposingCycleTestCaseBase, PeriodicProposalTestCaseMixin):
    def setUp(self):
        super(PopularProposalAnalyticsTestCase, self).setUp()
        self.set_proposals_and_data()

    def test_get_analytics_from_a_popular_proposal(self):
        self.assertEquals(self.popular_proposal.commitments_count, 1)
        self.assertEquals(self.popular_proposal.likers_count, 1)
        self.assertEquals(self.popular_proposal.visitors, 1)

    def test_get_analytics_with_timedelta(self):
        analytics = self.popular_proposal.get_analytics()
        self.assertEquals(analytics['commitments'], 1)
        self.assertEquals(analytics['visits'], 1)
        self.assertEquals(analytics['likers'], 1)

        analytics2 = self.popular_proposal.get_analytics(days=1)
        self.assertEquals(analytics2['commitments'], 0)
        self.assertEquals(analytics2['visits'], 0)
        self.assertEquals(analytics2['likers'], 0)


class PopularProposalPeriodicReporterTestCase(ProposingCycleTestCaseBase, PeriodicProposalTestCaseMixin):
    def setUp(self):
        super(PopularProposalPeriodicReporterTestCase, self).setUp()
        self.set_proposals_and_data()

    def test_instantiate_and_get_attributes(self):
        r = PeriodicReporter(self.fiera)
        self.assertEquals(r.mail_template, 'periodic_report')
        proposals = r.get_proposals()
        self.assertIn(self.popular_proposal, proposals)
        context = r.get_mail_context()
        self.assertEquals(context['user'], self.fiera)
        self.assertEquals(context['proposals'][0]['proposal'], self.popular_proposal)
        self.assertEquals(context['proposals'][0]['analytics'], self.popular_proposal.get_analytics())

    def test_get_context_for_only_one_day(self):
        r = PeriodicReporter(self.fiera, days=1)
        context = r.get_mail_context()
        self.assertEquals(context['proposals'][0]['analytics']['commitments'], 0)
        self.assertEquals(context['proposals'][0]['analytics']['visits'], 0)
        self.assertEquals(context['proposals'][0]['analytics']['likers'], 0)

    def test_send_mail(self):
        initial_amount_of_mails = len(mail.outbox)
        r = PeriodicReporter(self.fiera)
        r.send_mail()
        amount_of_mails = len(mail.outbox)
        self.assertEquals(amount_of_mails, initial_amount_of_mails + 1)
        the_mail = mail.outbox[amount_of_mails - 1]
        self.assertEquals(len(the_mail.to), 1)
        self.assertIn(self.fiera.email, the_mail.to)

    def test_not_send_anything_if_user_does_not_have_proposals(self):
        user = User.objects.create_user(username="newuser", email="user@github.com")
        initial_amount_of_mails = len(mail.outbox)
        r = PeriodicReporter(user)
        r.send_mail()
        amount_of_mails = len(mail.outbox)
        self.assertEquals(amount_of_mails, initial_amount_of_mails)


class PeriodicReporterTasksTestCase(ProposingCycleTestCaseBase, PeriodicProposalTestCaseMixin):
    def setUp(self):
        super(PeriodicReporterTasksTestCase, self).setUp()
        self.set_proposals_and_data()

    @override_config(PERIODIC_REPORTS_ENABLED=True)
    def test_task(self):
        User.objects.create_user(username="newuser", email="user@github.com")
        initial_amount_of_mails = len(mail.outbox)
        report_sender_task.delay()
        amount_of_mails = len(mail.outbox)
        self.assertGreater(amount_of_mails, initial_amount_of_mails)

    @override_config(PERIODIC_REPORTS_ENABLED=False)
    def test_task_with_periodic_reports_disabled(self):
        self.fiera.is_staff = False
        self.fiera.save()
        User.objects.create_user(username="newuser", email="user@github.com")
        initial_amount_of_mails = len(mail.outbox)
        report_sender_task.delay()
        amount_of_mails = len(mail.outbox)
        self.assertGreater(amount_of_mails, initial_amount_of_mails)
        ## Except if user is staff
        self.fiera.is_staff = True
        self.fiera.save()
        report_sender_task.delay()
        self.assertGreater(len(mail.outbox), initial_amount_of_mails)


class PopularProposalPeriodicReporterForOrganizationsTestCase(ProposingCycleTestCaseBase, PeriodicProposalTestCaseMixin):
    def setUp(self):
        super(PopularProposalPeriodicReporterForOrganizationsTestCase, self).setUp()
        self.set_proposals_and_data()
        self.fiera.profile.is_organization = True
        self.fiera.profile.save()
        self.popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                               area=self.arica,
                                                               data=self.data,
                                                               title=u'This is a title',
                                                               clasification=u'education'
                                                              )
        # This proposal has been liked by fiera (organization)
        # So it shouldn't be in the email
        self.should_not_be_in_recomendation = PopularProposal.objects.create(proposer=self.feli,
                                                                             area=self.arica,
                                                                             data=self.data,
                                                                             title=u'This is a title',
                                                                             clasification=u'education'
                                                                            )
        self.like = ProposalLike.objects.create(user=self.fiera,
                                                proposal=self.should_not_be_in_recomendation)
        # This proposal has the same classification as the one created by Fiera
        # 'educaion'
        # but has not been liked by Fiera, so it should be in the email
        self.should_be_1 = PopularProposal.objects.create(proposer=self.feli,
                                                                     area=self.arica,
                                                                     data=self.data,
                                                                     title=u'This is a title',
                                                                     clasification=u'education'
                                                                    )
        # This proposal does not have the same classification as the one created by Fiera
        # 'not_the_right_clasification'
        # and has not been liked by Fiera, so it should NOT be in the email
        self.should_not_be_in_recomendation2 = PopularProposal.objects.create(proposer=self.feli,
                                                                     area=self.arica,
                                                                     data=self.data,
                                                                     title=u'This is a title',
                                                                     clasification=u'not_the_right_clasification'
                                                                    )

    def test_recomendation_comes_with_new_proposals(self):
        should_not_be_1 = PopularProposal.objects.create(proposer=self.feli,
                                                         area=self.arica,
                                                         data=self.data,
                                                         title=u'old proposal',
                                                         clasification=u'education',
                                                        )
        should_not_be_1.created = TWO_DAYS_AGO
        should_not_be_1.save()

        r = PeriodicReporter(self.fiera, days=1)
        context = r.get_mail_context()
        new_proposals = context['new_proposals']
        self.assertIn(self.should_be_1, new_proposals)
        self.assertNotIn(self.should_not_be_in_recomendation, new_proposals)
        self.assertNotIn(self.should_not_be_in_recomendation2, new_proposals)
        self.assertNotIn(should_not_be_1, new_proposals)

    def test_sending_mail_with_recomendation_comes_with_new_proposals(self):
        initial_amount_of_mails = len(mail.outbox)
        r = PeriodicReporter(self.fiera)
        r.send_mail()
        amount_of_mails = len(mail.outbox)
        self.assertEquals(amount_of_mails, initial_amount_of_mails + 1)
