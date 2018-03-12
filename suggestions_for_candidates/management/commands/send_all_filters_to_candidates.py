# coding=utf-8
from django.core.management.base import BaseCommand
from suggestions_for_candidates.models import IncrementalsCandidateFilter


class Command(BaseCommand):
    help = u'Envía los mails con sugerencias de propuestas a los filtros de candidatos'

    def handle(self, *args, **options):
        for f in IncrementalsCandidateFilter.objects.all():
        	self.stdout.write('Enviando recomendaciones a ' + f.name)
        	f.send_mails(sleep=1)