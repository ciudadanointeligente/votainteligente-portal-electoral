# coding=utf-8
from .adapter_tests import MediaNaranjaAdaptersBase
from elections.models import Area
from medianaranja2.forms import SetupForm
from django.conf import settings


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
