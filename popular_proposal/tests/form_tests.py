# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from popular_proposal.forms import (ProposalForm,
                                    CommentsForm,
                                    RejectionForm)
from django.contrib.auth.models import User
from popolo.models import Area
from django.forms import CharField
from popular_proposal.models import ProposalTemporaryData
from django.core import mail
from django.template.loader import get_template
from django.template import Context


class FormTestCase(TestCase):
    def setUp(self):
        super(FormTestCase, self).setUp()
        self.fiera = User.objects.get(username='fiera')
        self.arica = Area.objects.get(id='arica-15101')
        self.data = {
            'email': u'fiera@ciudadanointeligente.org',
            'problem': u'A mi me gusta la contaminación de Santiago y los autos y sus estresantes ruedas',
            'solution': u'Viajar a ver al Feli una vez al mes',
            'when': u'1_year',
            'allies': u'El Feli y el resto de los cabros de la FCI'

        }
        self.feli = User.objects.get(username='feli')

    def test_instanciate_form(self):
        form = ProposalForm(data=self.data,
                            proposer=self.fiera,
                            area=self.arica)
        self.assertTrue(form.is_valid())
        cleaned_data = form.cleaned_data
        self.assertEquals(cleaned_data['problem'], self.data['problem'])
        self.assertEquals(cleaned_data['solution'], self.data['solution'])
        self.assertEquals(cleaned_data['when'], self.data['when'])
        self.assertEquals(cleaned_data['allies'], self.data['allies'])
        temporary_data = form.save()
        self.assertEquals(temporary_data.proposer, self.fiera)
        self.assertEquals(temporary_data.area, self.arica)
        t_data = temporary_data.data
        self.assertEquals(t_data['problem'], self.data['problem'])
        self.assertEquals(t_data['solution'], self.data['solution'])
        self.assertEquals(t_data['when'], self.data['when'])
        self.assertEquals(t_data['allies'], self.data['allies'])

    def test_comments_form(self):
        temporary_area = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                              area=self.arica,
                                                              data=self.data)
        form = CommentsForm(temporary_area=temporary_area,
                            moderator=self.feli)
        self.assertIsInstance(form.fields['problem'], CharField)
        self.assertIsInstance(form.fields['when'], CharField)
        self.assertIsInstance(form.fields['solution'], CharField)
        self.assertIsInstance(form.fields['allies'], CharField)

    def test_comments_form_saving(self):
        temporary_data = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                              area=self.arica,
                                                              data=self.data)
        data = {'problem': u'',
                'when': u'el plazo no está tan weno',
                'solution': u'',
                'allies': u'Los aliados podrían ser mejores'}


        form = CommentsForm(data=data,
                            moderator=self.feli,
                            temporary_area=temporary_data)
        self.assertTrue(form.is_valid())
        t_data = form.save()
        self.assertEquals(t_data.comments['when'], data['when'])
        self.assertEquals(t_data.comments['allies'], data['allies'])
        self.assertFalse(t_data.comments['problem'])
        self.assertFalse(t_data.comments['solution'])
        self.assertEquals(t_data.status, ProposalTemporaryData.Statuses.InTheirSide)

        #sends an email
        self.assertEquals(len(mail.outbox), 1)
        the_mail = mail.outbox[0]
        expected_context_data = {'when': {'original': temporary_data.data['when'],
                                          'comments': u'el plazo no está tan weno'},
                                 'allies': {'original': temporary_data.data['allies'],
                                            'comments': u'Los aliados podrían ser mejores'}}

        context = Context({'area': self.arica,
                           'temporary_data': temporary_data,
                           'moderator': self.feli,
                           'comments': expected_context_data
                          })

        template_body = get_template('mails/popular_proposal_moderation_body.html')
        template_subject = get_template('mails/popular_proposal_moderation_subject.html')
        expected_content= template_body.render(context)
        expected_subject = template_subject.render(context)
        self.assertTrue(the_mail.body)
        self.assertTrue(the_mail.subject)
        self.assertEquals(len(the_mail.to), 1)
        self.assertIn(self.fiera.email, the_mail.to)

    def test_rejection_form(self):
        temporary_data = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                              area=self.arica,
                                                              data=self.data)
        data = {'reason': u'No es un buen ejemplo'}
        form = RejectionForm(data=data,
                             moderator=self.feli,
                             temporary_area=temporary_data)
        self.assertTrue(form.is_valid())
        form.reject()
        temporary_data = ProposalTemporaryData.objects.get(id=temporary_data.id)
        self.assertEquals(temporary_data.status, ProposalTemporaryData.Statuses.Rejected)
        self.assertEquals(temporary_data.rejected_reason, data['reason'])

