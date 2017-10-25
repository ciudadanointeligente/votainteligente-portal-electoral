# coding=utf-8
from .adapter_tests import MediaNaranjaAdaptersBase
from elections.models import Area
from medianaranja2.forms import SetupForm, QuestionsForm, ProposalsForm
from django.conf import settings
from django import forms


class FormsTestCase(MediaNaranjaAdaptersBase):
    def setUp(self):
        super(FormsTestCase, self).setUp()
        self.setUpProposals()
        self.setUpQuestions()
        self.area = Area.objects.create(name="children",
                                        classification=settings.FILTERABLE_AREAS_TYPE[0])
        self.election.area = self.area
        self.election.save()

    def test_instanciate_category_selection_form(self):
        data = {
            'area': self.area.id,
            'categories': [self.category1.id, self.category2.id]
        }
        form = SetupForm(data)
        self.assertTrue(form.is_valid())
        self.assertEquals(form.cleaned_data['area'], self.area)
        self.assertIn(self.category1, form.cleaned_data['categories'])
        self.assertIn(self.category2, form.cleaned_data['categories'])

    def test_questions_form_instanciate(self):
        kwargs = {'categories': [self.category1, self.category2]}
        form = QuestionsForm(**kwargs)
        self.assertEquals(len(form.fields), 2)
        self.assertIn(self.topic1.slug, form.fields)
        self.assertIsInstance(form.fields[self.topic1.slug], forms.ModelChoiceField)
        topic_1_choices = list(form.fields[self.topic1.slug].choices)
        self.assertIn((self.position1.id, unicode(self.position1)), topic_1_choices)
        self.assertIn((self.position2.id, unicode(self.position2)), topic_1_choices)
        self.assertIn(self.topic2.slug, form.fields)
        self.assertIsInstance(form.fields[self.topic2.slug], forms.ModelChoiceField)
        topic_2_choices = list(form.fields[self.topic2.slug].choices)
        self.assertIn((self.position3.id, unicode(self.position3)), topic_2_choices)
        self.assertIn((self.position4.id, unicode(self.position4)), topic_2_choices)

    def test_get_cleaned_data_from_questions_form(self):
        data = {self.topic1.slug: self.position1.id,
                self.topic2.slug: self.position3.id}
        kwargs = {'categories': [self.category1, self.category2], 'data': data}
        form = QuestionsForm(**kwargs)
        self.assertTrue(form.is_bound)
        self.assertTrue(form.is_valid())
        self.assertIn(self.position1, form.cleaned_data['positions'])
        self.assertIn(self.position3, form.cleaned_data['positions'])

    def test_proposals_form_instanciate(self):
        kwargs = {'proposals': [self.p1, self.p2, self.p3]}
        form = ProposalsForm(**kwargs)
        proposals_choices = list(form.fields['proposals'].choices)
        self.assertIn((self.p1.id, unicode(self.p1)), proposals_choices)
        self.assertIn((self.p2.id, unicode(self.p2)), proposals_choices)
        self.assertIn((self.p3.id, unicode(self.p3)), proposals_choices)

    def test_posting_proposals_form(self):
        data = {'proposals': [self.p1.id, self.p2.id]}
        kwargs = {'proposals': [self.p1, self.p2, self.p3], 'data':data}
        form = ProposalsForm(**kwargs)
        self.assertTrue(form.is_bound)
        self.assertTrue(form.is_valid())
        self.assertIn(self.p1, form.cleaned_data['proposals'])
        self.assertIn(self.p1, form.cleaned_data['proposals'])
        