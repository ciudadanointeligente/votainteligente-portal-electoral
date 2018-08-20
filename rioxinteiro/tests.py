# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from rioxinteiro.tse_importer import TSEProcessorMixin
from django.core.management import call_command
from elections.models import Candidate, Election, Area
from constance.test import override_config

example_data = []

@override_config(DEFAULT_AREA='argentina')
class TSEParser(TestCase):
    def setUp(self):
        super(TSEParser, self).setUp()
        argentina = Area.objects.create(name=u'Argentina', id='argentina')
        Candidate.objects.all().delete()
        Election.objects.all().delete()

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