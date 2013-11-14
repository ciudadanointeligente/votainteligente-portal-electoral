# coding= utf-8
from django.core.management.base import BaseCommand, CommandError
from candideitorg.models import Candidate
import csv

class Command(BaseCommand):
    args = '<candidate photos csv file [,prepended url]>'

    def handle(self, *args, **options):
        file_path = args[0]
        prepended_url = ''
        if len(args) > 1:
            prepended_url += args[1]            
        tags_lines = csv.reader(open(file_path, 'rb'), delimiter=',')
        tags_lines.next()
        for line in tags_lines:
            candidate_name = line[0].decode('utf-8').strip()
            try:
                candidate = Candidate.objects.get(name=candidate_name)
                photo_url = prepended_url + line[1].decode('utf-8').strip()
                candidate.photo = photo_url
                candidate.save()
            except Candidate.DoesNotExist:
                print "The candidate %(candidate)s does not exist"%{
                    'candidate':candidate_name
                    }