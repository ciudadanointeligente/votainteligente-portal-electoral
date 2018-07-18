# coding=utf-8
from django.core.management.base import BaseCommand, CommandError
from elections.models import Election
from popular_proposal.models import PopularProposal
from popular_proposal.replicator import Replicator
from merepresenta.tse_processor import TSEProcessor

class Command(BaseCommand):
    help = u'Carga datos de los candidatos dado un archivo en formato CSV con separación de ;'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str)

    def handle(self, *args, **options):
        filename = options['filename']
        processor = TSEProcessor(filename)
        processor.process()
