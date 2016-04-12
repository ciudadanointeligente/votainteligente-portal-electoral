# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase as TestCase
from django.contrib.auth.models import User
from popular_proposal.models import PopularProposal, ProposalLike
#, SubscriptionEventBase
from popular_proposal.forms import SubscriptionForm
from unittest import skip
from django.core.urlresolvers import reverse
from django.template import Template, Context


class SubscribingToPopularProposal(TestCase):
    def setUp(self):
        super(SubscribingToPopularProposal, self).setUp()
        self.proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                       area=self.arica,
                                                       data=self.data,
                                                       title=u'This is a title'
                                                       )
        self.feli.set_password('alvarez')
        self.feli.save()

    def test_instanciate_liking_a_proposal(self):
        like = ProposalLike.objects.create(user=self.feli,
                                           proposal=self.proposal)
        self.assertTrue(like)
        self.assertTrue(like.created)
        self.assertTrue(like.updated)
        self.assertIn(self.feli, self.proposal.likers.all())

    def test_liking_also_has_a_subscription(self):
        like = ProposalLike.objects.create(user=self.fiera,
                                           proposal=self.proposal)

        self.assertTrue(like.subscription)
        subscription = like.subscription
        self.assertTrue(subscription.created)
        self.assertTrue(subscription.updated)

    def test_subscription_form(self):
        data = {}
        form = SubscriptionForm(data=data,
                                user=self.feli,
                                proposal=self.proposal)
        self.assertTrue(form.is_valid())
        form.subscribe()
        p = ProposalLike.objects.get(user=self.feli, proposal=self.proposal)
        self.assertTrue(p)

    def test_liking_view(self):
        url = reverse('popular_proposals:like_a_proposal', kwargs={'pk':self.proposal.id})
        self.client.login(username=self.feli,
                          password='alvarez')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('popular_proposal/new_subscription.html')
        response = self.client.post(url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'elections/area.html')
        self.assertEquals(response.context['proposal'], self.proposal)
        p = ProposalLike.objects.get(user=self.feli, proposal=self.proposal)
        self.assertTrue(p)

    def test_popular_proposal_likers(self):
        like = ProposalLike.objects.create(user=self.feli,
                                           proposal=self.proposal)
        template = Template(u"{% load votainteligente_extras %}{% if user|likes:proposal %}Sí{% else %}No{% endif %}")
        context = Context({
            'user': self.feli,
            'proposal': self.proposal
        })
        self.assertEquals(template.render(context), u"Sí")
        non_liker = User.objects.create_user(username='non_liker', password='s3cr3t')
        self.assertEquals(template.render(Context({'user':non_liker,
                                           'proposal':self.proposal})), u'No')

#class TheEventClass(SubscriptionEventBase):
#    class Meta:
#        proxy = True
#
#    def condition(subscription):
#        return True

@skip("Not yet")
class SubscriptionEventsTestCase(SubscribingToPopularProposal):
    def setUp(self):
        super(SubscriptionEventsTestCase, self).setUp()
        self.like = ProposalLike.objects.create(user=self.fiera,
                                                proposal=self.proposal)

    def test_instanciating_an_event(self):
        event = TheEventClass(subscription=self.like.subscription)
        event.save()
        self.assertFalse(event.notified)
        events = TheEventClass.get_ocurred_ones()
        self.assertTrue(events)
        self.assertIn(event, events)
        event.process()
        self.assertFalse(TheEventClass.objects.filter(id=event.id))
        self.assertTrue(event.notified)

    def test_subscription_can_have_events(self):
        event = TheEventClass(subscription=self.like.subscription)
        event.save()
        like = ProposalLike.objects.create(user=self.fiera,
                                           proposal=self.proposal)
        subscription = like.subscription
        subscription.events.add(event)

