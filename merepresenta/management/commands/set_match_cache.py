# coding=utf-8
from django.core.management.base import BaseCommand, CommandError
from merepresenta.match.matrix_builder import MatrixBuilder
from elections.models import Election
from popular_proposal.models import PopularProposal
from popular_proposal.replicator import Replicator
from merepresenta.tse_processor import TSEProcessor
from django.core.cache import cache


class Command(BaseCommand):
    help = u'Carga caché del match de merepresenta, esto es para que el match no toque la DB'

    def add_arguments(self, parser):
        parser.add_argument('time', type=int, default=7200, nargs="*")

    def handle(self, *args, **options):
        time = options['time'][0]
        cache.set('merepresenta_matrix_builder_setup_', None)
        cache.set('candidates_right_positions', None)
        builder = MatrixBuilder(time=time)
        r = builder.get_candidates_result()
        shape = r.shape
        self.stdout.write("Saved matrix of %d candidates with answers, for %d minutes" % (shape[0], time/60))
