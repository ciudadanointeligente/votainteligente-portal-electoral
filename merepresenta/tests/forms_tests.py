# coding=utf-8
from medianaranja2.tests.adapter_tests import MediaNaranjaAdaptersBase
from merepresenta.forms import MeRepresentaProposalsForm, MeRepresentaQuestionsForm
from elections.models import Area, QuestionCategory
from popular_proposal.models import PopularProposal
from django.conf import settings
from merepresenta.models import MeRepresentaPopularProposal
from django import forms


class ProposalsFormsTestCase(MediaNaranjaAdaptersBase):
    popular_proposal_class = MeRepresentaPopularProposal
    def setUp(self):
        super(ProposalsFormsTestCase, self).setUp()
        self.setUpProposals()
        self.area = Area.objects.create(name=u"children",
                                        classification=settings.FILTERABLE_AREAS_TYPE[0])
        self.election.area = self.area
        self.election.save()

    def test_proposals_form_instanciate(self):
        argentina = Area.objects.create(name=u'Argentina', id=u'argentina')
        proposals = MeRepresentaPopularProposal.objects.filter(id__in=[self.p1.id, self.p2.id, self.p3.id])
        kwargs = {'proposals': proposals}
        form = MeRepresentaProposalsForm(**kwargs)
        proposals_choices = list(form.fields['proposals'].choices)
        possible_labels = {}
        for t in proposals_choices:
            if type(t) == tuple:
                possible_labels[t[0]] = t[1]
        self.assertIn(unicode(self.p1), possible_labels[self.p1.id])
        self.assertIn(unicode(self.p2), possible_labels[self.p2.id])
        self.assertIn(unicode(self.p3), possible_labels[self.p3.id])
        areas = form.fields['area'].queryset.all()
        for a in areas:
            self.assertEquals(a.classification, settings.FILTERABLE_AREAS_TYPE[0])

class QuestionsFormTestCase(MediaNaranjaAdaptersBase):
    def setUp(self):
        super(QuestionsFormTestCase, self).setUp()
        QuestionCategory.objects.all().delete()
        self.setUpQuestions()
        QuestionCategory.objects.all().update(election=None)

    def test_instanciate_form(self):
        form = MeRepresentaQuestionsForm()
        self.assertEquals(len(form.fields), 4)
        self.assertIn(self.topic1.slug, form.fields)
        self.assertIsInstance(form.fields[self.topic1.slug], forms.ModelChoiceField)
        topic_1_choices = list(form.fields[self.topic1.slug].choices)
        self.assertIn((self.position1.id, self.position1.label), topic_1_choices)
        self.assertIn((self.position2.id, self.position2.label), topic_1_choices)
        self.assertIn(self.topic2.slug, form.fields)
        self.assertIsInstance(form.fields[self.topic2.slug], forms.ModelChoiceField)
        topic_2_choices = list(form.fields[self.topic2.slug].choices)
        self.assertIn((self.position3.id, self.position3.label), topic_2_choices)
        self.assertIn((self.position4.id, self.position4.label), topic_2_choices)
        areas = form.fields['area'].queryset.all()
        self.assertTrue(areas)
        for a in areas:
            self.assertEquals(a.classification, settings.FILTERABLE_AREAS_TYPE[0])

    def test_form_valid(self):
        a = Area.objects.filter(classification=settings.FILTERABLE_AREAS_TYPE[0]).first()
        data = {
            self.topic1.slug: self.position1.id,
            self.topic2.slug: self.position3.id,
            self.topic3.slug: self.position5.id,
            'area': a.id
        }
        form = MeRepresentaQuestionsForm(data=data)
        self.assertTrue(form.is_valid())
        cleaned_data = form.cleaned_data
        self.assertEquals(len(cleaned_data['positions']), 3)
        self.assertEquals(cleaned_data['area'], a)
