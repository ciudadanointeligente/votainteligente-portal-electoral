# coding= utf-8
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from elections.models import Election
import csv

class Command(BaseCommand):
  help = 'Carga informacion extra desde un CSV'

  def add_arguments(self, parser):
    parser.add_argument('csv_file', nargs='+', type=str)

  def handle(self, *args, **options):
    file_path = options['csv_file'][0]
    tags_lines = csv.reader(open(file_path, 'rb'), delimiter=',')
    # Remove header
    tags_lines.next()
    for line in tags_lines:
      if line:
        election_name, tags = line[0].decode('utf-8'), line[1]
        try:
          election = Election.objects.get(name=election_name)
          for tag in tags.split(','):
            tag = tag.decode('utf8').strip().lower()
            election.tags.add(tag)
        except Exception:
          print(u'excepción con la elección ' + election_name)
          pass
