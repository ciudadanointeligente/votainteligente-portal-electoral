# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from popular_proposal.forms import (get_form_list,
                                    wizard_forms_fields,
                                    get_user_organizations_choicefield)
from django.test import RequestFactory
from django.contrib.auth.models import User
from popolo.models import Area
from django import forms
from django.core.urlresolvers import reverse
from popular_proposal.forms.form_texts import TEXTS
from popular_proposal.models import ProposalTemporaryData
from django.core import mail
from backend_citizen.models import Organization, Enrollment
from collections import OrderedDict


USER_PASSWORD = 'secr3t'


class WizardTestCase(TestCase):
    def setUp(self):
        super(WizardTestCase, self).setUp()
        self.factory = RequestFactory()
        self.fiera = User.objects.get(username='fiera')
        self.arica = Area.objects.get(id='arica-15101')
        self.feli = User.objects.get(username='feli')
        self.feli.set_password(USER_PASSWORD)
        self.feli.save()
        ProposalTemporaryData.objects.all().delete()
        self.org = Organization.objects.create(name="Local Organization")

    def test_get_form_list(self):
        list_ = get_form_list()
        self.assertEquals(len(list_), len(wizard_forms_fields))
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
                self.assertTrue(f.fields[field].widget.attrs['long_text'])

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

    def test_return_user_organizations_field(self):
        field = get_user_organizations_choicefield(self.feli)
        self.assertIsNone(field)

        Enrollment.objects.create(user=self.feli,
                                  organization=self.org)
        field = get_user_organizations_choicefield(self.feli)
        self.assertIsInstance(field, forms.ChoiceField)
        self.assertEquals(len(field.choices), 2)
        empty_choice = field.choices[0]
        self.assertFalse(empty_choice[0])
        org_choice = field.choices[1]
        self.assertEquals(org_choice[0], self.org.id)
        self.assertEquals(org_choice[1], self.org.name)

    def test_instanciating_view(self):
        url = reverse('popular_proposals:propose_wizard',
                      kwargs={'slug': self.arica.id})
        self.client.login(username=self.feli,
                          password=USER_PASSWORD)

        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'popular_proposal/wizard/form_step.html')

    def get_example_data_for_post(self, t_response={}):
        cntr = len(t_response)
        for step in wizard_forms_fields:
            t_response[cntr] = {}
            for field in step['fields']:
                t_response[cntr][field] = ''
                field_dict = TEXTS.get(field, None)
                if field_dict:
                    help_text = field_dict.get('help_text', None)
                    if help_text:
                        t_response[cntr][str(cntr) + '-' + field] = help_text
                        t_response[cntr][field] = help_text
                    else:
                        t_response[cntr][str(cntr) + '-' + field] = field
                        t_response[cntr][field] = field
                else:
                    t_response[cntr]['fields'] = field

            cntr += 1
        return t_response

    def test_post_data_to_the_wizard(self):
        original_amount = len(mail.outbox)
        url = reverse('popular_proposals:propose_wizard',
                      kwargs={'slug': self.arica.id})
        self.client.login(username=self.feli,
                          password=USER_PASSWORD)
        test_response = self.get_example_data_for_post()
        response = self.client.get(url)
        steps = response.context['wizard']['steps']
        for i in range(steps.count):
            self.assertEquals(steps.current, unicode(i))
            data = test_response[i]
            data.update({'proposal_wizard-current_step': unicode(i)})
            response = self.client.post(url, data=data)
            self.assertEquals(response.context['area'], self.arica)
            is_done = False
            for template in response.templates:
                if template.name.endswith('done.html'):
                    is_done = True
            if not is_done:
                self.assertTrue(response.context['preview_data'])
            if 'form' in response.context:
                self.assertFalse(response.context['form'].errors)
                steps = response.context['wizard']['steps']
        self.assertTemplateUsed(response, 'popular_proposal/wizard/done.html')
        # Probar que se creó la promesa
        self.assertEquals(ProposalTemporaryData.objects.count(), 1)
        temporary_data = response.context['proposal']
        self.assertEquals(response.context['area'], self.arica)
        self.assertEquals(temporary_data.proposer, self.feli)
        self.assertEquals(temporary_data.area, self.arica)
        self.assertEquals(len(mail.outbox), original_amount + 1)

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

    def test_full_wizard(self):
        url = reverse('popular_proposals:propose_wizard_full')
        self.client.login(username=self.feli,
                          password=USER_PASSWORD)
        test_response = {0: {'0-area': self.arica.id}}
        test_response = self.get_example_data_for_post(test_response)
        response = self.client.get(url)
        steps = response.context['wizard']['steps']
        for i in range(steps.count):
            self.assertEquals(steps.current, unicode(i))
            data = test_response[i]
            data.update({'proposal_wizard_full-current_step': unicode(i)})
            response = self.client.post(url, data=data)
            if 'form' in response.context:
                self.assertFalse(response.context['form'].errors)
                steps = response.context['wizard']['steps']
        self.assertTemplateUsed(response, 'popular_proposal/wizard/done.html')
        # Probar que se creó la promesa
        self.assertEquals(ProposalTemporaryData.objects.count(), 1)
        temporary_data = response.context['proposal']
        self.assertEquals(response.context['area'], self.arica)
        self.assertEquals(temporary_data.proposer, self.feli)
        self.assertEquals(temporary_data.area, self.arica)
