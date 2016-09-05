# coding=utf-8
from django.core.management.base import BaseCommand
from elections.models import Election, QuestionCategory, Topic
import yaml


class Command(BaseCommand):
    help = u'Carga preguntas desde un yaml en todas las elecciones'

    def add_arguments(self, parser):
        parser.add_argument('archivo', type=str)

    def handle(self, *args, **options):
        file_name = options['archivo']
        data = None
        with open(file_name, 'r') as stream:
            try:
                data = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        for e in Election.objects.all():
            for category in data:
                cat = QuestionCategory.objects.create(election=e,
                                                      name=category['category_name'])
                for question in category['questions']:
                    t = Topic.objects.create(category=cat, label=question['question'])
                    for answer in question['answers']:
                        t.positions.create(label=answer)
