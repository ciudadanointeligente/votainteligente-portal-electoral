from django.core.management.base import BaseCommand
from backend_candidate.send_mails_to_candidates import send_user_to_candidate_from
from elections.models import Area
import time


class Command(BaseCommand):
    def handle(self, *args, **options):
        for area in Area.objects.exclude(elections__candidates__isnull=True):
            self.stdout.write('Enviando mails a los candidatos de ' + area.name)
            send_user_to_candidate_from(area)
            time.sleep(1)
