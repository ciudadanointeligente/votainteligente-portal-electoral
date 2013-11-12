# coding= utf-8
from django.core.management.base import BaseCommand, CommandError
from elections.models import VotaInteligenteMessage

class Command(BaseCommand):
    args = ''

    def handle(self, *args, **options):
        VotaInteligenteMessage.push_moderated_messages_to_writeit()