# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase
from proposal_subscriptions.models import SearchSubscription
from datetime import timedelta
from django.core.urlresolvers import reverse
import json
from proposal_subscriptions.views import OFTENITY_CHOICES


class CreateSubscriptionViewsTestCase(ProposingCycleTestCaseBase):
    def setUp(self):
        super(CreateSubscriptionViewsTestCase, self).setUp()
        self.feli.set_password('PASSWORD')
        self.feli.save()

    def test_get_the_url(self):
        url = reverse('proposal_subscriptions:subscribe')
        self.client.login(username=self.feli.username, password='PASSWORD')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        search_params_keys = json.loads(response.context['search_params_keys'])
        self.assertIn("text", search_params_keys)
        self.assertGreater(len(search_params_keys), 0)

    def test_only_logged_in_user_can_access_it(self):
        url = reverse('proposal_subscriptions:subscribe')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_post_creates_the_subscription(self):
        url = reverse('proposal_subscriptions:subscribe')
        self.client.login(username=self.feli.username, password='PASSWORD')
        data = {'oftenity': OFTENITY_CHOICES[0][0],
                'text': "bicicletas"}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        subscription = SearchSubscription.objects.get()
        self.assertEquals(subscription.user, self.feli)
        self.assertEquals(subscription.oftenity, timedelta(seconds=data['oftenity']))

        self.assertTrue(subscription.filter_class_module)
        self.assertTrue(subscription.filter_class_name)
        self.assertEquals(subscription.search_params, {'text': "bicicletas"})


class DeleteSubscriptionViewsTestCase(ProposingCycleTestCaseBase):
    def setUp(self):
        super(DeleteSubscriptionViewsTestCase, self).setUp()
        self.feli.set_password('PASSWORD')
        self.feli.save()
        self.subscription = SearchSubscription.objects.create(user=self.feli,
                                                              keyword_args={'perrito': "gatito"},
                                                              search_params={'text': "bicicletas"},
                                                              filter_class_module="popular_proposal.filters",
                                                              filter_class_name="ProposalWithoutAreaFilter",
                                                              oftenity=timedelta(weeks=1))

    def test_get_view(self):
        url = reverse('proposal_subscriptions:unsubscribe', kwargs={'token': self.subscription.token})
        self.client.login(username=self.feli.username, password='PASSWORD')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_post_view(self):
        url = reverse('proposal_subscriptions:unsubscribe', kwargs={'token': self.subscription.token})
        self.client.login(username=self.feli.username, password='PASSWORD')
        response = self.client.post(url)
        self.assertRedirects(response, reverse('popular_proposals:home'))


class SubscriptionListViewsTestCase(ProposingCycleTestCaseBase):
    def setUp(self):
        super(SubscriptionListViewsTestCase, self).setUp()
        self.feli.set_password('PASSWORD')
        self.feli.save()
        self.subscription = SearchSubscription.objects.create(user=self.feli,
                                                              keyword_args={'perrito': "gatito"},
                                                              search_params={'text': "bicicletas"},
                                                              filter_class_module="popular_proposal.filters",
                                                              filter_class_name="ProposalWithoutAreaFilter",
                                                              oftenity=timedelta(weeks=1))

    def test_get_list_view(self):
        subscription2 = SearchSubscription.objects.create(user=self.fiera,
                                                          keyword_args={'perrito': "gatito"},
                                                          search_params={'text': "bicicletas"},
                                                          filter_class_module="popular_proposal.filters",
                                                          filter_class_name="ProposalWithoutAreaFilter",
                                                          oftenity=timedelta(weeks=1))
        url = reverse('proposal_subscriptions:list')
        self.client.login(username=self.feli.username, password='PASSWORD')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.subscription, response.context['subscriptions'])
        self.assertNotIn(subscription2, response.context['subscriptions'])
