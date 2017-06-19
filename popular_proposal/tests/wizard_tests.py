# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from popular_proposal.forms import (get_form_list,
                                    AreaForm,
                                    wizard_forms_fields,
                                    get_user_organizations_choicefield)
from django.test import RequestFactory
from django.contrib.auth.models import User
from elections.models import Area, Candidate
from backend_candidate.models import Candidacy
from django import forms
from django.core.urlresolvers import reverse
from popular_proposal.forms.form_texts import TEXTS
from popular_proposal.models import ProposalTemporaryData, PopularProposal
from django.core import mail
from backend_citizen.models import Organization, Enrollment
from collections import OrderedDict
from constance.test import override_config
from django.test import override_settings
from constance import config

USER_PASSWORD = 'secr3t'


class WizardDataMixin(object):
    def get_example_data_for_post(self, **kwargs):
        test_response = kwargs.pop('test_response', {})
        cntr = len(test_response)
        for step in wizard_forms_fields:
            test_response[cntr] = {}
            for field in step['fields']:
                test_response[cntr][field] = ''
                field_dict = TEXTS.get(field, None)
                if field == "is_testing":
                    continue
                if field_dict:
                    help_text = field_dict.get('help_text', None)
                    if help_text:
                        test_response[cntr][str(cntr) + '-' + field] = help_text
                        test_response[cntr][field] = help_text
                    else:
                        test_response[cntr][str(cntr) + '-' + field] = field
                        test_response[cntr][field] = field
                else:
                    test_response[cntr]['fields'] = field

            cntr += 1
        return test_response


@override_settings(MODERATION_ENABLED=True)
class WizardTestCase(TestCase, WizardDataMixin):
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

    @override_config(PROPOSALS_ENABLED=False)
    def test_proposals_not_enabled(self):
        url = reverse('popular_proposals:propose_wizard',
                      kwargs={'slug': self.arica.id})
        self.client.login(username=self.feli,
                          password=USER_PASSWORD)

        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

        url = reverse('popular_proposals:propose_wizard_full')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_get_as_candidate_returns_404(self):
        url = reverse('popular_proposals:propose_wizard',
                      kwargs={'slug': self.arica.id})
        candidate = Candidate.objects.create(name='name')
        Candidacy.objects.create(candidate=candidate, user=self.feli)
        self.client.login(username=self.feli,
                          password=USER_PASSWORD)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

        url = reverse('popular_proposals:propose_wizard_full')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

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
            if 'form' in response.context and response.context['form'] is not None:
                self.assertFalse(response.context['form'].errors)
                steps = response.context['wizard']['steps']
        self.assertTemplateUsed(response, 'popular_proposal/wizard/done.html')
        # Probar que se creó la promesa
        self.assertEquals(ProposalTemporaryData.objects.count(), 1)
        temporary_data = response.context['popular_proposal']
        self.assertEquals(response.context['area'], self.arica)
        self.assertEquals(temporary_data.proposer, self.feli)
        self.assertEquals(temporary_data.area, self.arica)
        self.assertEquals(len(mail.outbox), original_amount + 2)

        the_mail = mail.outbox[original_amount + 1]
        self.assertIn(self.fiera.email, the_mail.to)
        self.assertIn(self.feli.email, the_mail.to)
        self.assertIn(str(temporary_data.id), the_mail.body)
        self.assertIn(temporary_data.get_title(), the_mail.body)
        self.assertIn(temporary_data.area.name, the_mail.subject)

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
        original_amount = len(mail.outbox)
        url = reverse('popular_proposals:propose_wizard_full')
        self.client.login(username=self.feli,
                          password=USER_PASSWORD)
        test_response = {0: {'0-area': self.arica.id}}
        test_response = self.get_example_data_for_post(test_response=test_response)
        response = self.client.get(url)
        steps = response.context['wizard']['steps']
        for i in range(steps.count):
            self.assertEquals(steps.current, unicode(i))
            data = test_response[i]
            data.update({'proposal_wizard_full-current_step': unicode(i)})
            response = self.client.post(url, data=data)
            self.assertEquals(response.context['area'], self.arica)

            if 'form' in response.context and response.context['form'] is not None:
                self.assertTrue(response.context['preview_data'])
                self.assertFalse(response.context['form'].errors)
                steps = response.context['wizard']['steps']
        self.assertTemplateUsed(response, 'popular_proposal/wizard/done.html')
        # Probar que se creó la promesa
        self.assertEquals(ProposalTemporaryData.objects.count(), 1)
        temporary_data = response.context['popular_proposal']
        self.assertEquals(response.context['area'], self.arica)
        self.assertEquals(temporary_data.proposer, self.feli)
        self.assertEquals(temporary_data.area, self.arica)
        self.assertEquals(len(mail.outbox), original_amount + 2)

        the_mail = mail.outbox[original_amount + 1]
        self.assertIn(self.fiera.email, the_mail.to)
        self.assertIn(self.feli.email, the_mail.to)
        self.assertIn(str(temporary_data.id), the_mail.body)
        self.assertIn(temporary_data.get_title(), the_mail.body)
        self.assertIn(temporary_data.area.name, the_mail.subject)

    @override_config(HIDDEN_AREAS='argentina')
    def test_full_wizard_get_area_form_kwargs(self):
        argentina = Area.objects.create(name=u'Argentina')
        url = reverse('popular_proposals:propose_wizard_full')
        self.feli.is_staff = True
        self.feli.save()
        self.client.login(username=self.feli,
                          password=USER_PASSWORD)
        test_response = {0: {'0-area': argentina}}
        test_response = self.get_example_data_for_post(test_response=test_response)
        response = self.client.get(url)
        area_form = response.context['form']
        area_field = area_form.fields['area']
        argentina_tuple = (argentina.id, argentina.name)
        self.assertIn(argentina_tuple, area_field.choices)


@override_config(DEFAULT_AREA='argentina')
class WizardTestCase2(TestCase, WizardDataMixin):
    def setUp(self):
        super(WizardTestCase2, self).setUp()
        self.fiera = User.objects.get(username='fiera')
        self.arica = Area.objects.get(id='arica-15101')
        self.feli = User.objects.get(username='feli')
        self.feli.set_password(USER_PASSWORD)
        self.feli.save()
        ProposalTemporaryData.objects.all().delete()
        self.org = Organization.objects.create(name="Local Organization")

    def test_full_wizard_without_areas(self):
        Area.objects.create(name=u'Argentina', id='argentina')
        original_amount = len(mail.outbox)
        url = reverse('popular_proposals:propose_wizard_full_without_area')
        self.client.login(username=self.feli,
                          password=USER_PASSWORD)
        test_response = self.get_example_data_for_post()
        response = self.client.get(url)
        self.assertNotIsInstance(response.context['form'], AreaForm)
        steps = response.context['wizard']['steps']
        for i in range(steps.count):
            self.assertEquals(steps.current, unicode(i))
            data = test_response[i]
            data.update({'proposal_wizard_full_without_area-current_step': unicode(i)})
            response = self.client.post(url, data=data)
            if 'form' in response.context:
                if response.context['form'] is not None:
                    self.assertFalse(response.context['form'].errors,
                                     u"Error en el paso" + unicode(i) + unicode(response.context['form'].errors))
                    self.assertTrue(response.context['preview_data'])
                    steps = response.context['wizard']['steps']
        self.assertTemplateUsed(response, 'popular_proposal/wizard/done.html')
        # Probar que se creó la promesa
        self.assertEquals(ProposalTemporaryData.objects.count(), 1)
        temporary_data = response.context['popular_proposal']
        self.assertEquals(temporary_data.proposer, self.feli)
        self.assertEquals(len(mail.outbox), original_amount + 2)

        the_mail = mail.outbox[original_amount + 1]
        self.assertIn(self.fiera.email, the_mail.to)
        self.assertIn(self.feli.email, the_mail.to)
        self.assertIn(str(temporary_data.id), the_mail.body)
        self.assertIn(temporary_data.get_title(), the_mail.body)


@override_config(DEFAULT_AREA='argentina')
class AutomaticallyCreateProposalTestCase(TestCase, WizardDataMixin):
    def setUp(self):
        super(AutomaticallyCreateProposalTestCase, self).setUp()
        self.fiera = User.objects.get(username='fiera')
        self.argentina = Area.objects.create(name=u'Argentina', id='argentina')
        self.feli = User.objects.get(username='feli')
        self.feli.set_password(USER_PASSWORD)
        self.feli.save()
        ProposalTemporaryData.objects.all().delete()
        self.url = reverse('popular_proposals:propose_wizard_full_without_area')
        self.example_data = self.get_example_data_for_post()

    def fill_the_whole_wizard(self, override_example_data={}, **kwargs):
        '''
        en:
        This method fills the whole wizard and returns the last response, in other words the done step.
        This method is designed to only work in testing environment.
        es-cl:
        Este método le completa todo el wizard y devuelve el response del final, es decir el done.
        Sólo funca para escribir tests.
        '''
        example_data = kwargs.pop("data", self.example_data)
        example_data.update(override_example_data	)
        url = kwargs.pop("url", self.url)
        user = kwargs.pop("user", self.feli)
        password = kwargs.pop("password", USER_PASSWORD)

        self.client.login(username=user,
                          password=password)
        response = self.client.get(url)
        steps = response.context['wizard']['steps']
        for i in range(steps.count):
            self.assertEquals(steps.current, unicode(i))
            data = example_data[i]
            data.update({'proposal_wizard_full_without_area-current_step': unicode(i)})
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

    def test_create_a_proposal(self):
        response = self.fill_the_whole_wizard()
        temporary_data = response.context['popular_proposal']
        temporary_data = ProposalTemporaryData.objects.get(id=temporary_data.id)
        with self.assertRaises(PopularProposal.DoesNotExist):
            temporary_data.created_proposal
        self.assertTrue(temporary_data.confirmation)
        self.assertFalse(temporary_data.confirmation.confirmed)

    def test_if_we_say_is_testing_in_wizard_it_creates_a_proposal_in_testing_area(self):
        try:
            testing_area = Area.objects.get(id=config.HIDDEN_AREAS)
        except Area.DoesNotExist:
            testing_area = Area.objects.create(id=config.HIDDEN_AREAS, name=config.HIDDEN_AREAS)
        response = self.fill_the_whole_wizard(override_example_data={4: {'4-title': 'title',
                                                                         '4-terms_and_conditions': True,
                                                                         "4-is_testing": True}})
        temporary_data = response.context['popular_proposal']

        self.assertEquals(temporary_data.area, testing_area)
