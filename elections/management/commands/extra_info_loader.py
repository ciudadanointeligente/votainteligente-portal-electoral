# coding= utf-8
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from elections.models import Election
import csv

class Command(BaseCommand):
	args = '<csv_file>'

	def handle(self, *args, **options):
		file_path = args[0]
		extrainfo = csv.reader(open(file_path, 'rb'), delimiter=',', quotechar='"', lineterminator='\n')
		# Remove header
		extrainfo.next()
		for line in extrainfo:
			if line:
				election_name, extra_info_title, extra_info_content = line[0].decode('utf-8').strip(), line[1].strip(), line[2].strip()
				try:
					election = Election.objects.get(name=election_name)
					election.extra_info_title = extra_info_title
					election.extra_info_content = extra_info_content
					election.save()
				except Exception,e:
					print u'excepción con la elección ' + election_name 
					print e
				