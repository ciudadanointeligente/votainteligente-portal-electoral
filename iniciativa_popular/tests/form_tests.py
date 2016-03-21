# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from iniciativa_popular.forms import ProposalForm
from django.contrib.auth.models import User
from popolo.models import Area


class FormTestCase(TestCase):
    def setUp(self):
        super(FormTestCase, self).setUp()

    def test_instanciate_form(self):
        fiera = User.objects.get(username='fiera')
        arica = Area.objects.get(id='arica-15101')
        data = {
            'your_name': u'Fiera Feroz',
            'email': u'fiera@ciudadanointeligente.org',
            'problem': u'A mi me gusta la contaminación de Santiago y los autos y sus estresantes ruedas',
            'solution': u'Viajar a ver al Feli una vez al mes',
            'when': u'1_year',
            'allies': u'El Feli y el resto de los cabros de la FCI'

        }
        form = ProposalForm(data=data, user=fiera, area=arica)
        self.assertTrue(form.is_valid())
        cleaned_data = form.cleaned_data
        self.assertEquals(cleaned_data['your_name'], data['your_name'])
        self.assertEquals(cleaned_data['problem'], data['problem'])
        self.assertEquals(cleaned_data['solution'], data['solution'])
        self.assertEquals(cleaned_data['when'], data['when'])
        self.assertEquals(cleaned_data['allies'], data['allies'])
        temporary_data = form.save()
        self.assertEquals(temporary_data.user, fiera)
        self.assertEquals(temporary_data.area, arica)
        t_data = temporary_data.data
        self.assertEquals(t_data['your_name'], data['your_name'])
        self.assertEquals(t_data['problem'], data['problem'])
        self.assertEquals(t_data['solution'], data['solution'])
        self.assertEquals(t_data['when'], data['when'])
        self.assertEquals(t_data['allies'], data['allies'])

