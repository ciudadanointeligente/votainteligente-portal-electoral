# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from popular_proposal.tests import ProposingCycleTestCaseBase
from popular_proposal.forms import (ProposalForm,
                                    CommentsForm,
                                    RejectionForm,
                                    ProposalTemporaryDataUpdateForm,
                                    get_form_list,
                                    wizard_forms_fields)
from votainteligente.facebook_page_getter import facebook_getter
import vcr
from django.test import RequestFactory
from django.contrib.auth.models import User
from popolo.models import Area
from django import forms


class WizardTestCase(TestCase):
    def setUp(self):
        super(WizardTestCase, self).setUp()
        self.factory = RequestFactory()
        self.fiera = User.objects.get(username='fiera')
        self.arica = Area.objects.get(id='arica-15101')
        self.feli = User.objects.get(username='feli')

    def test_get_form_list(self):
        list_ = get_form_list()
        self.assertEquals(len(list_), len(wizard_forms_fields))
        for step in list_:
            f = step()
            self.assertIsInstance(f, forms.Form)
            self.assertGreater(len(f.fields), 0)


#    def test_instanciating_view(self):
#        request = self.factory.get('/')
#        request.user = self.user
#        self.fail()
