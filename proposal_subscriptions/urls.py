from django.conf.urls import url
from proposal_subscriptions.views import SearchSubscriptionCreateView, SearchSubscriptionDeleteView

urlpatterns = [
    url(r'^subscribe/?$',
        SearchSubscriptionCreateView.as_view(),
        name='subscribe'),
    url(r'^unsubscribe/(?P<token>[-\w]+)/?$',
        SearchSubscriptionDeleteView.as_view(),
        name='unsubscribe'),
]
