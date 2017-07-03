from django.conf.urls import url
from proposal_subscriptions.views import SearchSubscriptionCreateView

urlpatterns = [
url(r'^subscribe/?$',
    SearchSubscriptionCreateView.as_view(),
    name='subscribe'),
]
