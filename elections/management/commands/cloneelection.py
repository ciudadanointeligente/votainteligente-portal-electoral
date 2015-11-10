from django.core.management.base import BaseCommand
from elections.models import Election
from elections.bin import SecondRoundCreator


class Command(BaseCommand):
    help = "Clones an election"

    def add_arguments(self, parser):
        parser.add_argument('election_slug', type=str)
        parser.add_argument('candidates_slug', nargs='+', type=str)

    def handle(self, *args, **options):
        election = Election.objects.get(slug=options['election_slug'])
        sc = SecondRoundCreator(election)
        for candidate_slug in options['candidates_slug']:
            candidate = election.candidates.get(id=candidate_slug)
            sc.pick_one(candidate)
        second_round = sc.get_second_round()
        self.stdout.write("Clone created with name %s and slug %s" % (second_round.name, second_round.slug))
        self.stdout.write("The url for it is %s" % (second_round.get_absolute_url()))


