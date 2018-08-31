from django.core.management.base import BaseCommand
from medianaranja2.candidate_proposals_matrix_generator import CandidateCommitmentsMatrixGenerator


class Command(BaseCommand):
    help = "Updates the cache for medianaranja"

    def add_arguments(self, parser):
        parser.add_argument('time', type=int, default=7200, nargs="*")

    def handle(self, *args, **options):
        matrix_generator = CandidateCommitmentsMatrixGenerator()
        time = options['time'][0]
        print time
        m = matrix_generator.set_cache(time)
        shape = m.shape
        self.stdout.write("Saved matrix of dimensions (%d, %d) for %d miliseconds" % (shape[0], shape[1], time))