# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase, override_settings
from rioxinteiro.tse_importer import TSEProcessorMixin
from django.core.management import call_command
from elections.models import Candidate, Election, Area
from constance.test import override_config
from django.core.validators import validate_email
validators = {
    'mail': validate_email
}

area_settings = {
    18:'slug',
    17:'area_name',
    23: 'election_name',
}
candidate_settings = {
    0: 'identifier',
    3: 'nome_completo',
    2: 'number',
    6: 'cpf',
    1: 'nome',
    12: 'job',
    5: 'date_of_birth',
    4: 'gender',
    11: 'education',
    8: 'civil_status',
    9: 'race',
    28: 'mail',
    21: 'img',

}
partido_settings = {
    25: 'number',
    27: 'name',
    26: 'initials'
}
coaligacao_settings = {
    22: "name",
    22: "partidos_coaligacao",
    22: "number"

}


_TSE_IMPORTER_CONF = {
    'area': area_settings,
    'candidate': candidate_settings,
    'partido': partido_settings,
    'coaligacao': coaligacao_settings
}

example_data = []

@override_config(DEFAULT_AREA='argentina')
class TSEParser(TestCase):
    def setUp(self):
        super(TSEParser, self).setUp()
        argentina = Area.objects.create(name=u'Argentina', id='argentina')
        Candidate.objects.all().delete()
        Election.objects.all().delete()

    @override_settings(TSE_IMPORTER_CONF=_TSE_IMPORTER_CONF)
    def test_calling_command(self):
        call_command('rio_import_from_tse', './rioxinteiro/fixtures/candidatos.csv')
        self.assertTrue(Candidate.objects.all())
        self.assertTrue(Election.objects.all())
    # @override_settings(FILTERABLE_AREAS_TYPE=['state',])
    # def test_creates_elements(self):
    #     rj_area = Area.objects.get(identifier='RJ')

    #     class JustForNowProcessor(TSEProcessorMixin):
    #         pass
    #     processor = JustForNowProcessor()
    #     result = processor.do_something(self.data)
    #     print result
    #     self.fail()