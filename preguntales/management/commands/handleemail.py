from django.core.management.base import BaseCommand
import sys
from preguntales.email_parser import EmailHandler


class Command(BaseCommand):
    args = ''
    help = 'Handles incoming EmailAnswer'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        lines = sys.stdin.readlines()
        handler = EmailHandler()
        answer = handler.handle(lines)
        answer.save()
