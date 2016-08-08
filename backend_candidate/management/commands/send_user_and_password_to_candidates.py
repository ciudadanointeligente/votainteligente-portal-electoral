from django.core.management.base import BaseCommand
from backend_candidate.send_mails_to_candidates import send_user_to_candidates


class Command(BaseCommand):
    def handle(self, *args, **options):
        send_user_to_candidates()