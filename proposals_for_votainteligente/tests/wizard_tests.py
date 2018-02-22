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
from popular_proposal.tests.wizard_tests import WizardDataMixin
from proposals_for_votainteligente.forms import (AreaForm)

USER_PASSWORD = 'secr3t'

class WithAreaProposalCreation(TestCase, WizardDataMixin):
    url = reverse('popular_proposals:propose_wizard_full_without_area')
    def setUp(self):
        super(WithAreaProposalCreation, self).setUp()
        self.fiera = User.objects.get(username='fiera')
        self.arica = Area.objects.get(id='arica-15101')
        self.feli = User.objects.get(username='feli')
        self.feli.set_password(USER_PASSWORD)
        self.feli.save()
        ProposalTemporaryData.objects.all().delete()

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

    def test_post_data_to_the_wizard_with_area(self):
        original_amount = len(mail.outbox)
        url = reverse('popular_proposals:propose_wizard',
                      kwargs={'slug': self.arica.id})
        self.client.login(username=self.feli,
                          password=USER_PASSWORD)
        test_response = self.get_example_data_for_post()
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        prefix = response.context['wizard']['management_form'].prefix
        steps = response.context['wizard']['steps']
        for i in range(steps.count):
            self.assertEquals(steps.current, unicode(i))
            data = test_response[i]
            data.update({prefix + '-current_step': unicode(i)})
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

    def test_full_wizard(self):
        original_amount = len(mail.outbox)
        url = reverse('popular_proposals:propose_wizard_full')
        self.client.login(username=self.feli,
                          password=USER_PASSWORD)
        test_response = {0: {'0-area': self.arica.id}}
        test_response = self.get_example_data_for_post(test_response=test_response)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        prefix = response.context['wizard']['management_form'].prefix
        steps = response.context['wizard']['steps']
        for i in range(steps.count):
            self.assertEquals(steps.current, unicode(i))
            data = test_response[i]
            data.update({prefix + '-current_step': unicode(i)})
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

@override_config(DEFAULT_AREA=u'argentina')
class WizardTestCase2(TestCase, WizardDataMixin):
    url = reverse('popular_proposals:propose_wizard_full_without_area')
    def setUp(self):
        super(WizardTestCase2, self).setUp()
        self.fiera = User.objects.get(username='fiera')
        self.arica = Area.objects.get(id='arica-15101')
        self.argentina = Area.objects.create(name=u'Argentina', id='argentina')
        self.feli = User.objects.get(username='feli')
        self.feli.set_password(USER_PASSWORD)
        self.feli.save()
        self.example_data = self.get_example_data_for_post()
        ProposalTemporaryData.objects.all().delete()

    def test_create_a_proposal_attributes(self):
        response = self.fill_the_whole_wizard()
        temporary_data = response.context['popular_proposal']
        proposal = temporary_data.created_proposal
        # Attributes of the proposal
        self.assertTrue(proposal.generated_at)

        
    def test_full_wizard_without_areas(self):
        original_amount = len(mail.outbox)
        url = reverse('popular_proposals:propose_wizard_full_without_area')
        self.client.login(username=self.feli,
                          password=USER_PASSWORD)
        test_response = self.get_example_data_for_post()
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        prefix = response.context['wizard']['management_form'].prefix
        self.assertNotIsInstance(response.context['form'], AreaForm)
        steps = response.context['wizard']['steps']
        for i in range(steps.count):
            self.assertEquals(steps.current, unicode(i))
            data = test_response[i]
            data.update({prefix + '-current_step': unicode(i)})
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
        self.assertEquals(temporary_data.area, self.argentina)
        self.assertEquals(len(mail.outbox), original_amount + 2)

        the_mail = mail.outbox[original_amount + 1]
        self.assertIn(self.fiera.email, the_mail.to)
        self.assertIn(self.feli.email, the_mail.to)
        self.assertIn(str(temporary_data.id), the_mail.body)
        self.assertIn(temporary_data.get_title(), the_mail.body)
