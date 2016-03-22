# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from popular_proposal.forms import ProposalForm, CommentsForm
from django.contrib.auth.models import User
from popolo.models import Area
from django.forms import CharField
from popular_proposal.models import ProposalTemporaryData

class FormTestCase(TestCase):
    def setUp(self):
        super(FormTestCase, self).setUp()
        self.fiera = User.objects.get(username='fiera')
        self.arica = Area.objects.get(id='arica-15101')
        self.data = {
            'your_name': u'Fiera Feroz',
            'email': u'fiera@ciudadanointeligente.org',
            'problem': u'A mi me gusta la contaminación de Santiago y los autos y sus estresantes ruedas',
            'solution': u'Viajar a ver al Feli una vez al mes',
            'when': u'1_year',
            'allies': u'El Feli y el resto de los cabros de la FCI'

        }

    def test_instanciate_form(self):
        form = ProposalForm(data=self.data,
                            user=self.fiera,
                            area=self.arica)
        self.assertTrue(form.is_valid())
        cleaned_data = form.cleaned_data
        self.assertEquals(cleaned_data['your_name'], self.data['your_name'])
        self.assertEquals(cleaned_data['problem'], self.data['problem'])
        self.assertEquals(cleaned_data['solution'], self.data['solution'])
        self.assertEquals(cleaned_data['when'], self.data['when'])
        self.assertEquals(cleaned_data['allies'], self.data['allies'])
        temporary_data = form.save()
        self.assertEquals(temporary_data.user, self.fiera)
        self.assertEquals(temporary_data.area, self.arica)
        t_data = temporary_data.data
        self.assertEquals(t_data['your_name'], self.data['your_name'])
        self.assertEquals(t_data['problem'], self.data['problem'])
        self.assertEquals(t_data['solution'], self.data['solution'])
        self.assertEquals(t_data['when'], self.data['when'])
        self.assertEquals(t_data['allies'], self.data['allies'])

    def test_comments_form(self):
        temporary_area = ProposalTemporaryData.objects.create(user=self.fiera,
                                                              area=self.arica,
                                                              data=self.data)
        form = CommentsForm(temporary_area=temporary_area)
        self.assertIsInstance(form.fields['problem'], CharField)
        self.assertIsInstance(form.fields['when'], CharField)
        self.assertIsInstance(form.fields['solution'], CharField)
        self.assertIsInstance(form.fields['allies'], CharField)
