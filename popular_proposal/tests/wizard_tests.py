# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from popular_proposal.forms import (get_form_list,
                                    wizard_forms_fields,)
from django.test import RequestFactory
from django.contrib.auth.models import User
from elections.models import Area, Candidate
from backend_candidate.models import Candidacy
from django import forms
from django.core.urlresolvers import reverse
from popular_proposal.forms import UpdateProposalForm
from popular_proposal.forms.form_texts import TEXTS
from popular_proposal.models import ProposalTemporaryData
from django.core import mail
from collections import OrderedDict
from constance.test import override_config
from django.test import override_settings
from constance import config
from popular_proposal.tests import example_fields

USER_PASSWORD = 'secr3t'


class WizardDataMixin(object):
    url = reverse('popular_proposals:propose_wizard_full_without_area')
    wizard_forms_fields =  wizard_forms_fields
    def get_example_data_for_post(self, **kwargs):
        test_response = kwargs.pop('test_response', {})
        cntr = len(test_response)
        for step in self.wizard_forms_fields:
            test_response[cntr] = {}
            for field in step['fields']:
                test_response[cntr][field] = ''
                field_dict = TEXTS.get(field, None)
                if field == "is_testing":
                    continue
                field_type = step['fields'][field].__class__.__name__

                if field_type in ['ChoiceField']:
                    test_response[cntr][str(cntr) + '-' + field] = step['fields'][field].choices[-1][0]
                    test_response[cntr][field] = step['fields'][field].choices[-1][0]
                elif field_type in ['ModelChoiceField']:
                    choice = step['fields'][field].queryset.last().id
                    test_response[cntr][str(cntr) + '-' + field] = choice
                    test_response[cntr][field] = choice
                elif field_dict:
                    help_text = example_fields.get(field_type, None)
                    test_response[cntr][str(cntr) + '-' + field] = help_text
                    test_response[cntr][field] = help_text
                else:
                    test_response[cntr]['fields'] = field

            cntr += 1
        return test_response

    def fill_the_whole_wizard(self,
                              override_example_data={},
                              **kwargs):
        '''
        en:
        This method fills the whole wizard and returns the last response, in other words the done step.
        This method is designed to only work in testing environment.
        es-cl:
        Este método le completa todo el wizard y devuelve el response del final, es decir el done.
        Sólo funca para escribir tests.
        '''
        example_data = kwargs.pop("data", self.example_data)
        example_data.update(override_example_data)
        url = kwargs.pop("url", self.url)
        user = kwargs.pop("user", self.feli)
        password = kwargs.pop("password", USER_PASSWORD)

        self.client.login(username=user,
                          password=password)
        response = self.client.get(url)
        prefix = response.context['wizard']['management_form'].prefix
        self.assertEquals(response.status_code, 200)
        steps = response.context['wizard']['steps']
        for i in range(steps.count):
            self.assertEquals(steps.current, unicode(i))
            data = example_data[i]
            data.update({prefix + '-current_step': unicode(i)})
            response = self.client.post(url, data=data)
            if 'form' in response.context:
                if response.context['form'] is not None:
                    self.assertFalse(response.context['form'].errors,
                                     u"Error en el paso" + unicode(i) + unicode(response.context['form'].errors))
                    self.assertTrue(response.context['preview_data'])
                    steps = response.context['wizard']['steps']
        is_done = False
        for template in response.templates:
            if template.name.endswith('done.html'):
                is_done = True
        self.assertTrue(is_done)
        return response


@override_settings(MODERATION_ENABLED=True)
class WizardTestCase(TestCase, WizardDataMixin):
    def setUp(self):
        super(WizardTestCase, self).setUp()
        self.factory = RequestFactory()
        self.fiera = User.objects.get(username='fiera')
        self.feli = User.objects.get(username='feli')
        self.feli.set_password(USER_PASSWORD)
        self.feli.save()
        ProposalTemporaryData.objects.all().delete()

    def test_get_form_list(self):
        list_ = get_form_list()
        self.assertEquals(len(list_), len(self.wizard_forms_fields))
        for step in list_:
            f = step()
            self.assertIsInstance(f, forms.Form)
            self.assertGreater(len(f.fields), 0)

    def test_get_texts_for_forms(self):
        list_ = get_form_list()
        for step in list_:
            f = step()
            for field in f.fields:
                self.assertTrue(f.explanation_template)

    @override_settings(WIZARD_FORM_MODIFIER=None)
    def test_get_form_list_depending_on_user(self):
        def return_none(user=None):
            return None

        def return_boolean_field(user=None):
            if user == self.feli:
                return forms.BooleanField()
            return None
        form_fields = [{'template': 'popular_proposal/wizard/paso5.html',
                        'explation_template': "popular_proposal/steps/p.html",
                        'fields': OrderedDict([
                            ('test', return_boolean_field),
                            ('testb', return_none)
                        ])
                        }
                       ]
        list_ = get_form_list(form_fields, user=self.feli)
        all_fields = list_[0].base_fields.items()
        self.assertEquals(all_fields[0][0], 'test')
        test_field = all_fields[0][1]
        self.assertIsInstance(test_field,
                              forms.BooleanField)
        self.assertEquals(len(all_fields), 1)

    def test_user_should_accept_terms_and_conditions(self):
        list_ = get_form_list()
        form_class = list_[-1]
        test_response = self.get_example_data_for_post()
        data = test_response[len(test_response) - 1]
        for key in data.keys():
            if 'terms_and_conditions' in key:
                data[key] = False
        form = form_class(data=data)

        self.assertFalse(form.is_valid())
        for key in data.keys():
            if 'terms_and_conditions' in key:
                data[key] = True
        form = form_class(data=data)
        self.assertTrue(form.is_valid())


class AutomaticallyCreateProposalTestCase(TestCase, WizardDataMixin):
    def setUp(self):
        super(AutomaticallyCreateProposalTestCase, self).setUp()
        self.fiera = User.objects.get(username='fiera')
        self.feli = User.objects.get(username='feli')
        self.feli.set_password(USER_PASSWORD)
        self.feli.save()
        ProposalTemporaryData.objects.all().delete()
        self.url = reverse('popular_proposals:create')
        self.example_data = self.get_example_data_for_post()

    def test_create_a_proposal(self):
        original_amount = len(mail.outbox)
        response = self.fill_the_whole_wizard()
        temporary_data = response.context['popular_proposal']
        temporary_data = ProposalTemporaryData.objects.get(id=temporary_data.id)
        self.assertTrue(temporary_data.created_proposal)
        '''
        Hay dos mails el primero es para la persona que propone y el segundo
        es para el equipo donde les avisamos que hay una propuesta nueva
        '''
        expected_number_of_emails = 2
        self.assertEquals(len(mail.outbox), original_amount + expected_number_of_emails)
        url_in_mail = False
        for i in range(expected_number_of_emails):
            the_mail = mail.outbox[original_amount]
            if temporary_data.created_proposal.get_absolute_url() in the_mail.body:
                url_in_mail = True
        self.assertTrue(url_in_mail)

    def test_create_a_proposal_attributes(self):
        response = self.fill_the_whole_wizard()
        temporary_data = response.context['popular_proposal']
        proposal = temporary_data.created_proposal
        # Attributes of the proposal
        self.assertTrue(proposal.is_local_meeting)

    def test_done_brings_update_proposal_form(self):
        response = self.fill_the_whole_wizard()
        temporary_data = response.context['popular_proposal']

        form = response.context['form_update']
        self.assertIsInstance(form, UpdateProposalForm)
        self.assertEquals(form.instance, temporary_data.created_proposal)

