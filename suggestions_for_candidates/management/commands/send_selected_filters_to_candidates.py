# coding=utf-8
from django.core.management.base import BaseCommand
from suggestions_for_candidates.models import IncrementalsCandidateFilter


class Command(BaseCommand):
    help = u'Envía los mails con sugerencias de propuestas a los filtros de candidatos seleccionados'

    def add_arguments(self, parser):
        parser.add_argument('filter_ids', nargs='+', type=str)


    def handle(self, *args, **options):
        ids = [int(id) for id in options['filter_ids']]
        for f in IncrementalsCandidateFilter.objects.filter(id__in=ids):
            self.stdout.write('Enviando recomendaciones a ' + f.name)
            f.send_mails(sleep=1)