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
