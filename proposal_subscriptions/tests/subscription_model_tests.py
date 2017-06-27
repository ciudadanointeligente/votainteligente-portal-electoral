# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase
from proposal_subscriptions.models import SearchSubscription
from datetime import timedelta


class SearchSubscriptionModel(ProposingCycleTestCaseBase):
    def setUp(self):
        super(SearchSubscriptionModel, self).setUp()


    def test_instanciate(self):
        subscription = SearchSubscription.objects.create(user=self.feli,
                                                         keyword_args={'perrito': "gatito" },
                                                         search_params={'text': "bicicletas"},
                                                         filter_class_module="popular_proposal.filters",
                                                         filter_class_name="TextSearchForm",
                                                         oftenity=timedelta(weeks=1))

        self.assertTrue(subscription.created)
        self.assertIsNone(subscription.last_run)
