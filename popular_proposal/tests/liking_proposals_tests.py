# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase as TestCase
from django.contrib.auth.models import User
from popular_proposal.models import (ProposalLike,
                                     PopularProposal,
                                     )
import json
from popular_proposal.forms import SubscriptionForm
from django.core.urlresolvers import reverse
from django.template import Template, Context


class SubscribingToPopularProposal(TestCase):
    def setUp(self):
        super(SubscribingToPopularProposal, self).setUp()
        self.proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                       data=self.data,
                                                       title=u'This is a title'
                                                       )
        self.feli.set_password('alvarez')
        self.feli.save()
        self.fiera.set_password('feroz')
        self.fiera.save()

    def test_instanciate_liking_a_proposal(self):
        like = ProposalLike.objects.create(user=self.feli,
                                           message=u"Hello we like your proposal so please contact us",
                                           proposal=self.proposal)
        self.assertTrue(like)
        self.assertTrue(like.created)
        self.assertTrue(like.updated)
        self.assertIn(self.feli, self.proposal.likers.all())

    def test_subscription_form(self):
        data = {}
        form = SubscriptionForm(data=data,
                                user=self.feli,
                                proposal=self.proposal)
        self.assertTrue(form.is_valid())
        form.subscribe()
        p = ProposalLike.objects.get(user=self.feli, proposal=self.proposal)
        self.assertTrue(p)

    def test_subscription_form_with_message(self):
        message = u'This is a message'
        data = {'message': message}
        form = SubscriptionForm(data=data,
                                user=self.feli,
                                proposal=self.proposal)
        self.assertTrue(form.is_valid())
        form.subscribe()
        p = ProposalLike.objects.get(user=self.feli, proposal=self.proposal)
        self.assertEquals(p.message, message)

    def test_liking_view(self):
        url = reverse('popular_proposals:like_a_proposal', kwargs={'pk': self.proposal.id})
        self.client.login(username=self.feli,
                          password='alvarez')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('popular_proposal/new_subscription.html')
        response = self.client.post(url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['proposal'], self.proposal)
        p = ProposalLike.objects.get(user=self.feli, proposal=self.proposal)
        self.assertTrue(p)

    def test_liking_redirecting_view(self):
        url_home = reverse('popular_proposals:home')
        kwargs = {'pk': self.proposal.id}
        url = reverse('popular_proposals:like_a_proposal',
                      kwargs=kwargs)
        self.client.login(username=self.feli,
                          password='alvarez')
        response_get = self.client.get(url, {'next': url_home})
        self.assertEquals(response_get.context['next'], url_home)
        response = self.client.post(url,
                                    data={'next': url_home})
        self.assertNotEquals(response.status_code, 302)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'popular_proposal/subscribing_result.html')
        self.assertIn('proposal', response.context)
        self.assertEquals(response.context['proposal'], self.proposal)
        like = ProposalLike.objects.get(proposal=self.proposal)
        self.assertEquals(response.context['like'], like)

    def test_not_liking_twice(self):
        url_home = reverse('popular_proposals:home')
        kwargs = {'pk': self.proposal.id}
        url = reverse('popular_proposals:like_a_proposal',
                      kwargs=kwargs)
        self.client.login(username=self.feli,
                          password='alvarez')
        response_get = self.client.get(url, {'next': url_home})
        self.assertEquals(response_get.context['next'], url_home)
        self.client.post(url,
                         data={'next': url_home})
        proposals = ProposalLike.objects.filter(user=self.feli, proposal=self.proposal)
        self.assertEquals(proposals.count(), 1)

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
        self.assertEquals(template.render(Context({'user': non_liker,
                                          'proposal': self.proposal})), u'No')
        template = Template(u"{% load votainteligente_extras %}{% with  user|support:proposal as support %}{{support.id}} {{support.user}}{% endwith %}")
        self.assertEquals(template.render(context), str(like.id) + " " + self.feli.username)

    def test_unlike(self):
        like = ProposalLike.objects.create(user=self.feli,
                                           proposal=self.proposal)
        url = reverse('popular_proposals:unlike_proposal', kwargs={'pk': like.id})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)
        self.client.login(username=self.fiera,
                          password='feroz')
        response = self.client.post(url)
        self.assertEquals(response.status_code, 404)
        self.client.login(username=self.feli,
                          password='alvarez')
        response = self.client.post(url)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(ProposalLike.objects.filter(id=like.id))
        content = json.loads(response.content)
        self.assertEquals(int(content['deleted_item']), like.id)

    def test_like_str(self):
        like = ProposalLike.objects.create(user=self.feli,
                                           message=u"Hello we like your proposal so please contact us",
                                           proposal=self.proposal)
        self.assertTrue(like.__str__())
