# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase
from popular_proposal.forms import (ProposalForm,
                                    CommentsForm,
                                    RejectionForm,
                                    ProposalTemporaryDataUpdateForm,
                                    ProposalTemporaryDataModelForm,
                                    FIELDS_TO_BE_AVOIDED,
                                    UpdateProposalForm,
                                    AuthorityNotCommitingForm)
from popular_proposal.forms.form_texts import TOPIC_CHOICES_DICT
from django.contrib.auth.models import User
from django.forms import CharField
from popular_proposal.models import (ProposalTemporaryData,
                                     PopularProposal)
from django.core import mail
from django.template.loader import get_template
from django.template import Context, Template
from popular_proposal.forms import (WHEN_CHOICES,
                                    AuthorityCommitmentForm)
from popular_proposal.forms.form_texts import TEXTS
from django.core.urlresolvers import reverse
from django.test import override_settings
from constance.test import override_config
from popular_proposal import get_authority_model


authority_model = get_authority_model()


class FormTestCase(ProposingCycleTestCaseBase):
    def setUp(self):
        super(FormTestCase, self).setUp()
        self.fiera = User.objects.get(username='fiera')
        self.feli = User.objects.get(username='feli')
        self.load = '{% load votainteligente_extras %}'

    def test_instanciate_form(self):
        original_amount = len(mail.outbox)
        form = ProposalForm(data=self.data,
                            proposer=self.fiera)
        self.assertTrue(form.is_valid(), form.errors)
        cleaned_data = form.cleaned_data
        self.assertEquals(cleaned_data['title'], self.data['title'])
        self.assertEquals(cleaned_data['problem'], self.data['problem'])
        self.assertEquals(cleaned_data['when'], self.data['when'])
        self.assertEquals(cleaned_data['causes'], self.data['causes'])
        temporary_data = form.save()
        self.assertEquals(len(mail.outbox), original_amount + 1)
        self.assertEquals(temporary_data.proposer, self.fiera) 
        t_data = temporary_data.data
        self.assertEquals(t_data['problem'], self.data['problem'])
        self.assertEquals(t_data['when'], self.data['when'])
        self.assertEquals(t_data['causes'], self.data['causes'])

    def test_comments_form(self):
        t_data = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                      data=self.data)
        form = CommentsForm(temporary_data=t_data,
                            moderator=self.feli)
        self.assertIsInstance(form.fields['problem'], CharField)
        self.assertIsInstance(form.fields['when'], CharField)
        self.assertIsInstance(form.fields['causes'], CharField)

    def test_comments_form_saving(self):
        t_data = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                      data=self.data)
        data = {'problem': u'',
                'clasification': '',
                'when': u'el plazo no está tan weno',
                'causes': u'mejora esto'}

        form = CommentsForm(data=data,
                            moderator=self.feli,
                            temporary_data=t_data)
        self.assertTrue(form.is_valid(), form.errors)
        t_data = form.save()
        self.assertEquals(t_data.comments['when'], data['when'])
        self.assertEquals(t_data.comments['causes'], data['causes'])
        self.assertFalse(t_data.comments['problem'])
        self.assertEquals(t_data.status,
                          ProposalTemporaryData.Statuses.InTheirSide)

        # sends an email
        self.assertEquals(len(mail.outbox), 1)
        the_mail = mail.outbox[0]
        self.assertTrue(the_mail.body)
        self.assertTrue(the_mail.subject)
        self.assertEquals(len(the_mail.to), 1)
        self.assertIn(self.fiera.email, the_mail.to)

    def test_comments_form_with_previous_comments_in(self):
        comments = {
            'problem': '',
            'when': u'El plazo no está tan bueno',
            'causes': ''
        }
        in_their_side = ProposalTemporaryData.Statuses.InTheirSide
        t_data = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                      data=self.data,
                                                      comments=comments,
                                                      status=in_their_side)
        form = CommentsForm(moderator=self.feli,
                            temporary_data=t_data)

        self.assertIn(comments['when'], form.fields['when'].help_text)

    def test_rejection_form(self):
        t_data = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                      data=self.data)
        data = {'reason': u'No es un buen ejemplo'}
        form = RejectionForm(data=data,
                             moderator=self.feli,
                             temporary_data=t_data)
        self.assertTrue(form.is_valid(), form.errors)
        form.reject()
        temporary_data = ProposalTemporaryData.objects.get(id=t_data.id)
        self.assertEquals(temporary_data.status,
                          ProposalTemporaryData.Statuses.Rejected)
        self.assertEquals(temporary_data.rejected_reason, data['reason'])

    def test_update_temporary_popular_proposal(self):
        theirside_status = ProposalTemporaryData.Statuses.InTheirSide
        t_data = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                      data=self.data,
                                                      comments=self.comments,
                                                      status=theirside_status)
        data = self.data
        data['overall_comments'] = u"Quizás sea una buena idea que revises si \
        conviene el plazo de un año"
        form = ProposalTemporaryDataUpdateForm(data=data,
                                               temporary_data=t_data,
                                               proposer=self.fiera)
        self.assertTrue(form.initial)
        self.assertIn(self.comments['when'], form.fields['when'].help_text)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEquals(form.get_overall_comments(),
                          data['overall_comments'])
        t_data = form.save()
        t_data = ProposalTemporaryData.objects.get(id=t_data.id)
        overall_comments = data.pop('overall_comments')
        for key in data.keys():
            if key in FIELDS_TO_BE_AVOIDED:
                continue
            self.assertEquals(t_data.data[key], data[key])
        self.assertEquals(t_data.status,
                          ProposalTemporaryData.Statuses.InOurSide)
        self.assertEquals(t_data.overall_comments, overall_comments)

    def test_form_fields(self):
        theirside_status = ProposalTemporaryData.Statuses.InTheirSide
        t_data = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                      data=self.data,
                                                      comments=self.comments,
                                                      status=theirside_status)
        data = self.data
        data['overall_comments'] = u"Quizás sea una buena idea que revises si \
        conviene el plazo de un año"
        form = ProposalTemporaryDataUpdateForm(data=data,
                                               temporary_data=t_data,
                                               proposer=self.fiera)
        self.assertNotIn('terms_and_conditions', form.fields)
        first_field = form.fields.popitem(last=False)
        # Because the field when has comments this should be the firstone
        self.assertEquals(first_field[0], 'when')
        last_field = form.fields.popitem()
        self.assertEquals(last_field[0], 'overall_comments')

    def test_when_template_tag(self):
        choice = WHEN_CHOICES[1]
        template = Template(
            self.load + "{{ '1_year'|popular_proposal_when }}")
        self.assertEquals(template.render(Context({})), choice[1])
        template = Template(
            self.load + "{{ 'perrito'|popular_proposal_when }}")
        self.assertEquals(template.render(Context({})), 'perrito')

    def test_form_questions_template_tag(self):
        question = TEXTS['problem']['preview_question']
        template = Template(
            self.load + "{{ 'problem'|popular_proposal_question }}")
        self.assertEquals(template.render(Context({})), question)
        template = Template(
            self.load + "{{ 'perrito'|popular_proposal_question }}")
        self.assertEquals(template.render(Context({})), 'perrito')

    def test_get_all_types_of_questions(self):
        t_data = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                      data=self.data)
        template_str = get_template('popular_proposal/_extra_info.html')
        rendered_template = template_str.render({'texts': TEXTS,
                                                 'data': self.data})
        template = Template(
            self.load + "{% get_questions_and_descriptions popular_proposal %}")
        actual = template.render(Context({'popular_proposal': t_data}))
        self.assertEquals(rendered_template, actual)

    def test_get_classification_str(self):
        key = 'espaciospublicos'
        clasification = TOPIC_CHOICES_DICT[key]
        template = Template(
            self.load + "{{ choice_id|get_classification_from_str }}")
        actual = template.render(Context({'choice_id': key}))
        self.assertEquals(clasification, actual)


class UpdateFormTestCase(ProposingCycleTestCaseBase):
    def setUp(self):
        super(UpdateFormTestCase, self).setUp()
        self.image = self.get_image()
        self.popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                               data=self.data,
                                                               title=u'This is a title'
                                                               )
        self.feli = User.objects.get(username='feli')
        self.feli.set_password('secr3t')
        self.feli.save()
        self.fiera.set_password('feroz')
        self.fiera.save()

    def test_instanciate_form(self):
        update_data = {'background': u'Esto es un antecedente',
                       'contact_details': u'Me puedes contactar en el teléfono 123456',
                       }
        file_data = {'image': self.image,
                     'document': self.get_document()}
        form = UpdateProposalForm(data=update_data,
                                  files=file_data,
                                  instance=self.popular_proposal)
        self.assertTrue(form.is_valid(), form.errors)
        proposal = form.save()
        self.assertEquals(proposal.background, update_data['background'])
        self.assertTrue(proposal.image)
        self.assertTrue(proposal.document)
        self.assertEquals(proposal.contact_details, update_data['contact_details'])

    @override_settings(PROPOSAL_UPDATE_FORM=None)
    def test_get_update_view(self):
        url = reverse('popular_proposals:citizen_update', kwargs={'slug': self.popular_proposal.slug})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)
        self.client.login(username=self.feli.username, password='secr3t')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)
        self.client.login(username=self.fiera.username, password='feroz')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['popular_proposal'], self.popular_proposal)
        self.assertTemplateUsed(response, 'popular_proposal/update.html')
        self.assertIsInstance(response.context['form'], UpdateProposalForm)

    def test_post_update_view(self):
        url = reverse('popular_proposals:citizen_update', kwargs={'slug': self.popular_proposal.slug})
        kwargs = {'data': {'background': u'Esto es un antecedente',
                           'contact_details': u'Me puedes contactar en el teléfono 123456'},
                  'files': {'image': self.image,
                            'document': self.get_document()}}
        self.client.login(username=self.fiera.username, password='feroz')
        response = self.client.post(url, **kwargs)
        detail_url = reverse('popular_proposals:detail', kwargs={'slug': self.popular_proposal.slug})
        self.assertRedirects(response, detail_url)


class ModelFormTest(ProposingCycleTestCaseBase):
    def setUp(self):
        super(ModelFormTest, self).setUp()

    def test_form_has_all_fields(self):
        t_data = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                      data=self.data)
        form = ProposalTemporaryDataModelForm(instance=t_data)
        for key in self.data.keys():
            self.assertIn(key, form.fields.keys())
            self.assertEquals(self.data[key], form.fields[key].initial)

    def test_form_saving_data(self):
        t_data = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                      data=self.data)
        data = self.data
        data['title'] = u'Título título'
        data['proposer'] = self.fiera.id
        data['status'] = t_data.status
        form = ProposalTemporaryDataModelForm(instance=t_data, data=data)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        temporary_data = ProposalTemporaryData.objects.get(id=t_data.id)
        self.assertEquals(temporary_data.data['title'], data['title'])


class AuthorityCommitmentTestCase(ProposingCycleTestCaseBase):
    def setUp(self):
        super(AuthorityCommitmentTestCase, self).setUp()
        self.authority = authority_model.objects.first()
        self.proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                       data=self.data,
                                                       title=u'This is a title'
                                                       )
        self.feli.set_password('alvarez')
        self.feli.save()
        self.fiera.set_password('feroz')
        self.fiera.save()

    def test_instanciating_form(self):
        data = {'terms_and_conditions': True, 'detail': 'Esto es un detalle'}
        form = AuthorityCommitmentForm(authority=self.authority,
                                       proposal=self.proposal,
                                       data=data)
        self.assertTrue(form.is_valid(), form.errors)
        commitment = form.save()
        self.assertEquals(commitment.proposal, self.proposal)
        self.assertEquals(commitment.authority, self.authority)
        self.assertEquals(commitment.detail, data['detail'])
        self.assertTrue(commitment.commited)

    def test_instanciating_form_with_no_commiting(self):
        data = {'detail': 'Yo me comprometo',
                'terms_and_conditions': True}
        form = AuthorityNotCommitingForm(authority=self.authority,
                                         proposal=self.proposal,
                                         data=data)
        self.assertTrue(form.is_valid(), form.errors)
        commitment = form.save()
        self.assertEquals(commitment.proposal, self.proposal)
        self.assertEquals(commitment.authority, self.authority)
        self.assertEquals(commitment.detail, data['detail'])
        self.assertFalse(commitment.commited)

