from django.core.management.base import BaseCommand, CommandError
from elections.models import Election
from popular_proposal.models import PopularProposal
from popular_proposal.replicator import Replicator

class Command(BaseCommand):
    help = 'Replicates a proposal in all areas except in the excluded ids'

    def add_arguments(self, parser):
        parser.add_argument('popular_proposal_slug', type=str)
        parser.add_argument('excluded_area_ids', nargs='*', type=str)

    def handle(self, *args, **options):
        exclude = options['excluded_area_ids']
        proposal = PopularProposal.objects.get(slug=options['popular_proposal_slug'])
        replicator = Replicator(proposal)
        replicator.replicate(exclude=exclude)
