# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase
from popular_proposal.tests.wizard_tests import WizardDataMixin
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from votita.models import KidsProposal, KidsGathering


USER_PASSWORD = 'secr3t'


class GateheringCreateViewTestCase(ProposingCycleTestCaseBase, WizardDataMixin):
    def setUp(self):
        super(GateheringCreateViewTestCase, self).setUp()
        self.feli = User.objects.get(username='feli')
        self.feli.set_password(USER_PASSWORD)
        self.feli.save()

    def test_get_to_create_a_gathering(self):
        self.client.login(username=self.feli.username, password=USER_PASSWORD)
        url = reverse('votita:create_gathering')
        print url
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_creating_proposal_for_gathering_get_view(self):
        gathering = KidsGathering.objects.create(name=u"Título")
        url = reverse('votita:proposal_for_gathering',
                      kwargs={'pk':gathering.id})
        self.client.login(username=self.feli.username, password=USER_PASSWORD)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertIn('formset', response.context)
        formset = response.context['formset']
        self.assertEquals(formset.instance, gathering)
        formset.model = KidsProposal
        form = formset.forms

    def test_creating_proposal_for_gathering_post_view(self):
        gathering = KidsGathering.objects.create(name=u"Título")
        url = reverse('votita:proposal_for_gathering',
                      kwargs={'pk':gathering.id})

        self.client.login(username=self.feli.username, password=USER_PASSWORD)
        data = {'proposals-0-title': "perrito",
                "proposals-1-gathering": 1,
                "proposals-TOTAL_FORMS": 1,
                "proposals-INITIAL_FORMS": 0,
                "proposals-MIN_NUM_FORMS": 1,
                "proposals-MAX_NUM_FORMS": 1000
                }
        response = self.client.post(url, data=data)

        proposal = KidsProposal.objects.get(gathering=gathering)
        self.assertEquals(proposal.title, data['proposals-0-title'])
        self.assertEquals(proposal.proposer, self.feli)
