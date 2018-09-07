from django.core.management.base import BaseCommand
from medianaranja2.candidate_proposals_matrix_generator import CandidateCommitmentsMatrixGenerator, OrganizationMatrixCreator


class Command(BaseCommand):
    help = "Updates the cache for medianaranja"

    def add_arguments(self, parser):
        parser.add_argument('time', type=int, default=7200, nargs="*")

    def handle(self, *args, **options):
        matrix_generator = CandidateCommitmentsMatrixGenerator()
        time = options['time'][0]
        m = matrix_generator.set_cache(time)
        shape = m.shape

        self.stdout.write("Saved matrix of candidates and commitments of dimensions (%d, %d) for %d minutes" % (shape[0], shape[1], time/60))
        o_m = OrganizationMatrixCreator()
        o_m.set_cache(time)
        shape = o_m.main_matrix.shape
        self.stdout.write("Saved matrix of organizations and interactions of dimensions (%d, %d) for %d minutes" % (shape[0], shape[1], time/60))
