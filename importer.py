# coding=utf-8
import csv, codecs
from elections.models import Candidate, Election, PersonalData, Area
from django.core.urlresolvers import reverse
from backend_candidate.models import CandidacyContact


def process_candidates():
    reader = codecs.open("candidates.csv", 'r', encoding='utf-8')
    counter = 0
    candidates_ids = []
    for line in reader:
        row = line.split(u',')
        area_name = row[0].title().strip()
        try:
            area = Area.objects.get(name__iexact=area_name)
        except Exception as e:
            print area_name
            print e
        kind_of = row[1].title().strip()
        election_name = kind_of + u' por ' + area.name
        if not Election.objects.filter(name__iexact=election_name):
            print u"no pillé a " + election_name
            Candidate.objects.filter(id__in=candidates_ids).delete()
            return
        else:
            e = Election.objects.get(name__iexact=election_name)
        name = row[2].title().strip()
        candidate = Candidate(name=name)

        candidate.save()
        candidates_ids.append(candidate.id)
        e.candidates.add(candidate)
        try:
            mail = row[6].strip().lower()
        except IndexError:
            mail = None
        if mail:
            contact = CandidacyContact.objects.create(candidate=candidate,
                                                      mail=mail)

        pacto = row[3].strip().title()
        sub_pacto = row[4].strip().title()
        partido = row[5].strip().title()
        if pacto:
            PersonalData.objects.create(candidate=candidate,
                                        label=u'Pacto',
                                        value=pacto)
        if sub_pacto:
            PersonalData.objects.create(candidate=candidate,
                                        label=u'Sub Pacto',
                                        value=sub_pacto)
        if partido:
            PersonalData.objects.create(candidate=candidate,
                                        label=u'Partido',
                                        value=partido)

        counter += 1
        if not counter % 1000:
            print u'van' + str(counter)

def process_areas():
    reader = codecs.open("candidates.csv", 'r', encoding='utf-8')
    not_found_areas = []
    for line in reader:
        row = line.split(u',')
        area_name = row[0].title().strip()
        try:
            area = Area.objects.get(name__iexact=area_name)
        except Exception as e:
            if area_name not in not_found_areas:
                not_found_areas.append(area_name)
    print not_found_areas

def check_if_candidates_exists():
    reader = codecs.open("candidates.csv", 'r', encoding='utf-8')
    existing_candidates = []
    for line in reader:
        row = line.split(u',')
        name = row[2].title().strip()
        previous_candidates = Candidate.objects.filter(name=name)
        if previous_candidates:
            print previous_candidates
            existing_candidates.append(previous_candidates.first())

    print existing_candidates
