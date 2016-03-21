# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from iniciativa_popular.forms import ProposalForm


class FormTestCase(TestCase):
    def setUp(self):
        super(FormTestCase, self).setUp()

    def test_instanciate_form(self):
        data = {
            'your_name': u'Fiera Feroz',
            'email': u'fiera@ciudadanointeligente.org',
            'problem': u'A mi me gusta la contaminación de Santiago y los autos y sus estresantes ruedas',
            'solution': u'Viajar a ver al Feli una vez al mes',
            'when': u'1_year',
            'allies': u'El Feli y el resto de los cabros de la FCI'

        }
        form = ProposalForm(data=data)
        self.assertTrue(form.is_valid())
        cleaned_data = form.cleaned_data
        self.assertEquals(cleaned_data['your_name'], data['your_name'])
        self.assertEquals(cleaned_data['email'], data['email'])
        self.assertEquals(cleaned_data['problem'], data['problem'])
        self.assertEquals(cleaned_data['solution'], data['solution'])
        self.assertEquals(cleaned_data['when'], data['when'])
        self.assertEquals(cleaned_data['allies'], data['allies'])

