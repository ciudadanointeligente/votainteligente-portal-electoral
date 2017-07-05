# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase
from proposal_subscriptions.models import SearchSubscription
from datetime import timedelta
from popular_proposal.models import PopularProposal
from django.contrib.auth.models import User
from proposal_subscriptions.runner import SubscriptionRunner, TaskRunner
from django.utils import timezone
from popular_proposal.forms.form_texts import TOPIC_CHOICES
from django.core import mail
from django.core.urlresolvers import reverse


class SearchSubscriptionModel(ProposingCycleTestCaseBase):
    def setUp(self):
        super(SearchSubscriptionModel, self).setUp()

    def test_instanciate(self):
        subscription = SearchSubscription.objects.create(user=self.feli,
                                                         keyword_args={'perrito': "gatito"},
                                                         search_params={'text': "bicicletas"},
                                                         filter_class_module="popular_proposal.filters",
                                                         filter_class_name="ProposalWithoutAreaFilter",
                                                         oftenity=timedelta(weeks=1))

        self.assertTrue(subscription.created)
        self.assertIsNone(subscription.last_run)
        self.assertTrue(subscription.token)
        self.assertEquals(len(str(subscription.token)), 36)

    def test_unsubscribe_url(self):
        subscription = SearchSubscription.objects.create(user=self.feli,
                                                         keyword_args={'perrito': "gatito"},
                                                         search_params={'text': "bicicletas"},
                                                         filter_class_module="popular_proposal.filters",
                                                         filter_class_name="ProposalWithoutAreaFilter",
                                                         oftenity=timedelta(weeks=1))
        expected_url = reverse('proposal_subscriptions:unsubscribe', kwargs={'token': subscription.token})
        self.assertEquals(subscription.unsubscribe_url(), expected_url)

    def test_run_sends_hits_to_user(self):
        a_week_ago = timezone.now() - timedelta(weeks=1)
        not_a_hit = PopularProposal.objects.create(proposer=self.fiera,
                                                   area=self.arica,
                                                   data=self.data,
                                                   title=u'bicicletas',
                                                   clasification=TOPIC_CHOICES[1][0],
                                                   )
        not_a_hit.created = a_week_ago
        not_a_hit.updated = a_week_ago
        not_a_hit.save()
        subscription = SearchSubscription.objects.create(user=self.feli,
                                                         keyword_args={},
                                                         search_params={'text': "bicicletas"},
                                                         filter_class_module="popular_proposal.filters",
                                                         filter_class_name="ProposalWithoutAreaFilter",
                                                         oftenity=timedelta(seconds=1))
        hit_one = PopularProposal.objects.create(proposer=self.fiera,
                                                 area=self.arica,
                                                 data=self.data,
                                                 title=u'bicicletas',
                                                 clasification=TOPIC_CHOICES[1][0],
                                                 )
        not_a_hit_b = PopularProposal.objects.create(proposer=self.fiera,
                                                     area=self.arica,
                                                     data=self.data,
                                                     title=u'perritos',
                                                     clasification=TOPIC_CHOICES[1][0],
                                                     )
        qs = subscription.base_queryset()
        self.assertIn(hit_one, qs.all())
        self.assertIn(not_a_hit, qs.all())
        self.assertNotIn(not_a_hit_b, qs.all())
        self.assertEquals(qs.count(), 2)
        # filtering according to time
        qs = subscription.queryset()
        self.assertIn(hit_one, qs)
        self.assertEquals(len(qs), 1)


class SearchSubscriptionRunner(ProposingCycleTestCaseBase):
    def setUp(self):
        super(SearchSubscriptionRunner, self).setUp()
        a_week_ago = timezone.now() - timedelta(weeks=1)
        self.not_a_hit = PopularProposal.objects.create(proposer=self.fiera,
                                                        area=self.arica,
                                                        data=self.data,
                                                        title=u'bicicletas',
                                                        clasification=TOPIC_CHOICES[1][0],
                                                        )
        self.not_a_hit.created = a_week_ago
        self.not_a_hit.updated = a_week_ago
        self.not_a_hit.save()

        self.hit_one = PopularProposal.objects.create(proposer=self.fiera,
                                                      area=self.arica,
                                                      data=self.data,
                                                      title=u'bicicletas',
                                                      clasification=TOPIC_CHOICES[1][0],
                                                      )
        self.not_a_hit_b = PopularProposal.objects.create(proposer=self.fiera,
                                                          area=self.arica,
                                                          data=self.data,
                                                          title=u'perritos',
                                                          clasification=TOPIC_CHOICES[1][0],
                                                          )

    def test_one_user_two_subscriptions(self):
        two_days_ago = timezone.now() - timedelta(days=2)
        hit_two = PopularProposal.objects.create(proposer=self.fiera,
                                                 area=self.arica,
                                                 data=self.data,
                                                 title=u'bicicletas',
                                                 clasification=TOPIC_CHOICES[2][0],
                                                 )
        s1 = SearchSubscription.objects.create(user=self.feli,
                                               keyword_args={},
                                               search_params={'text': "bicicletas"},
                                               filter_class_module="popular_proposal.filters",
                                               filter_class_name="ProposalWithoutAreaFilter",
                                               oftenity=timedelta(seconds=1))
        s1.created = two_days_ago
        s1.save()
        s2 = SearchSubscription.objects.create(user=self.feli,
                                               keyword_args={},
                                               search_params={'text': "bicicletas",
                                                              'clasification': TOPIC_CHOICES[2][0]},
                                               filter_class_module="popular_proposal.filters",
                                               filter_class_name="ProposalWithoutAreaFilter",
                                               oftenity=timedelta(seconds=1))
        s2.created = two_days_ago
        s2.save()
        runner = SubscriptionRunner(self.feli)
        qs = runner.get_proposals()
        self.assertIn(self.hit_one, qs)
        self.assertIn(hit_two, qs)
        self.assertEquals(len(qs), 2)

    def test_get_subscriptions(self):
        a_day_ago = timezone.now() - timedelta(days=1)
        two_days_ago = timezone.now() - timedelta(days=2)
        # s1 should be in
        s1 = SearchSubscription.objects.create(user=self.feli,
                                               keyword_args={},
                                               search_params={'text': "bicicletas"},
                                               filter_class_module="popular_proposal.filters",
                                               filter_class_name="ProposalWithoutAreaFilter",
                                               last_run=a_day_ago,
                                               oftenity=timedelta(seconds=1))
        s1.created = two_days_ago
        s1.save()
        # s2 should NOT be in
        s2 = SearchSubscription.objects.create(user=self.feli,
                                               keyword_args={},
                                               search_params={'text': "bicicletas",
                                                              'clasification': TOPIC_CHOICES[2][0]},
                                               filter_class_module="popular_proposal.filters",
                                               filter_class_name="ProposalWithoutAreaFilter",
                                               last_run=a_day_ago,
                                               oftenity=timedelta(days=2))
        s2.created = two_days_ago
        s2.save()
        # s3 should be in
        s3 = SearchSubscription.objects.create(user=self.feli,
                                               keyword_args={},
                                               search_params={'text': "bicicletas",
                                                              'clasification': TOPIC_CHOICES[2][0]},
                                               filter_class_module="popular_proposal.filters",
                                               filter_class_name="ProposalWithoutAreaFilter",
                                               oftenity=timedelta(hours=1))
        s3.created = two_days_ago
        s3.save()
        # s4 should NOT be in
        s4 = SearchSubscription.objects.create(user=self.feli,
                                               keyword_args={},
                                               search_params={'text': "bicicletas",
                                                              'clasification': TOPIC_CHOICES[2][0]},
                                               filter_class_module="popular_proposal.filters",
                                               filter_class_name="ProposalWithoutAreaFilter",
                                               oftenity=timedelta(days=2))
        s4.created = a_day_ago
        s4.save()
        runner = SubscriptionRunner(self.feli)
        qs = runner.get_subscriptions()
        self.assertNotIn(s4, qs.all())
        self.assertIn(s3, qs.all())
        self.assertIn(s1, qs.all())
        self.assertNotIn(s2, qs.all())

    def test_send_mail_with_data(self):
        original_amount_of_mails = len(mail.outbox)
        a_week_ago = timezone.now() - timedelta(weeks=1)
        PopularProposal.objects.create(proposer=self.fiera,
                                       data=self.data,
                                       title=u'bicicletas',
                                       clasification=TOPIC_CHOICES[2][0],
                                       )
        s = SearchSubscription.objects.create(user=self.feli,
                                              keyword_args={},
                                              search_params={'text': "bicicletas",
                                                             'clasification': TOPIC_CHOICES[2][0]},
                                              filter_class_module="popular_proposal.filters",
                                              filter_class_name="ProposalWithoutAreaFilter",
                                              oftenity=timedelta(days=1))
        s.created = a_week_ago
        s.save()
        runner = SubscriptionRunner(self.feli)
        result = runner.send()
        self.assertTrue(result)
        self.assertEquals(len(mail.outbox), original_amount_of_mails + 1)
        the_mail = mail.outbox[original_amount_of_mails]
        self.assertIn(self.feli.email, the_mail.to)
        self.assertEquals(len(the_mail.to), 1)

        self.assertIn(reverse('proposal_subscriptions:list'), the_mail.body)

    def test_if_there_are_no_subscriptions_no_mails_are_sent(self):
        original_amount_of_mails = len(mail.outbox)
        runner = SubscriptionRunner(self.feli)
        result = runner.send()
        self.assertFalse(result)
        self.assertEquals(len(mail.outbox), original_amount_of_mails)


class SearchSubscriptionTaskRunner(ProposingCycleTestCaseBase):
    def setUp(self):
        super(SearchSubscriptionTaskRunner, self).setUp()

    def test_get_the_right_users(self):
        User.objects.create_user(username="1")
        User.objects.create_user(username="2")
        User.objects.create_user(username="3")
        SearchSubscription.objects.create(user=self.feli,
                                          keyword_args={},
                                          search_params={'text': "bicicletas"},
                                          filter_class_module="popular_proposal.filters",
                                          filter_class_name="ProposalWithoutAreaFilter",
                                          oftenity=timedelta(seconds=1))
        tr = TaskRunner()
        self.assertIn(self.feli, tr.users())
        self.assertEquals(len(tr.users()), 1)

    def test_send_subscription_notifications(self):
        original_amount_of_mails = len(mail.outbox)
        a_week_ago = timezone.now() - timedelta(weeks=1)
        PopularProposal.objects.create(proposer=self.fiera,
                                       data=self.data,
                                       title=u'bicicletas',
                                       clasification=TOPIC_CHOICES[2][0],
                                       )
        s = SearchSubscription.objects.create(user=self.feli,
                                              keyword_args={},
                                              search_params={'text': "bicicletas",
                                                             'clasification': TOPIC_CHOICES[2][0]},
                                              filter_class_module="popular_proposal.filters",
                                              filter_class_name="ProposalWithoutAreaFilter",
                                              oftenity=timedelta(days=1))
        s.created = a_week_ago
        s.save()
        tr = TaskRunner()
        tr.send()
        self.assertEquals(len(mail.outbox), original_amount_of_mails + 1)
        the_mail = mail.outbox[original_amount_of_mails]
        self.assertIn(self.feli.email, the_mail.to)
        self.assertEquals(len(the_mail.to), 1)
