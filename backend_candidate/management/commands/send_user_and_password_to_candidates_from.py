# coding=utf-8
from django.core.management.base import BaseCommand
from backend_candidate.send_mails_to_candidates import send_user_to_candidate_from
from elections.models import Area


class Command(BaseCommand):
    help = u'Envía mails con usuario y password a los candidatos de esta area'

    def add_arguments(self, parser):
        parser.add_argument('area_id', nargs='+', type=str)

    def handle(self, *args, **options):
        for area_id in options['area_id']:
            area = Area.objects.get(id=area_id)
            send_user_to_candidate_from(area)