# coding=utf-8
from django.core.management.base import BaseCommand
from elections.models import Candidate
from backend_candidate.models import add_contact_and_send_mail


class Command(BaseCommand):
    help = u'Envía un mail a un candiato con su mail y password'

    def add_arguments(self, parser):
        parser.add_argument('mail', type=str)
        parser.add_argument('candidate_slug', type=str)

    def handle(self, *args, **options):
        mail = options['mail']
        candidate = Candidate.objects.get(slug=options['candidate_slug'])
        self.stdout.write(u'Enviando mail a ' + candidate.name + u' la dirección es: ' + mail)
        add_contact_and_send_mail(mail, candidate)
