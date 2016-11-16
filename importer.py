# coding=utf-8
import codecs
from elections.models import Candidate, Election, PersonalData, Area
from django.core.urlresolvers import reverse
from backend_candidate.models import CandidacyContact
import unicodecsv as csv
from django.utils.text import slugify
from backend_candidate.models import send_candidate_username_and_password
from popular_proposal.models import PopularProposal
from popular_proposal.exporter import CommitmentsExporter


def area_getter(area_name):
    try:
        area = Area.objects.get(name=area_name)
        return area
    except Exception as e:
        posible_area_id = slugify(area_name)
        try:
            area = Area.objects.get(id__icontains=posible_area_id)
            return area
        except Exception as e:
            return None


def process_candidates_with_names():
    reader = codecs.open("candidatos_y_mails.csv", 'r', encoding='utf-8')
    counter = 0
    candidates_ids = []
    for line in reader:
        row = line.split(u',')
        area_name = row[0].title().strip()
        kind_of = row[1].title().strip()
        election_name = kind_of + u' por ' + area_name
        try:
            e = Election.objects.get(name__iexact=election_name)
        except:
            print election_name + u' no encontrada'
            continue

        candidate_name = row[2].title().strip()

        candidates = e.candidates.filter(name__icontains=candidate_name)
        if candidates.count() > 1:
            print candidate_name + u' está más de una vez'
            continue
        elif not candidates.count():
            print candidate_name + u' no está'
            continue
        candidate = candidates.first()
        try:
            mail = row[3].strip().lower()
        except IndexError:
            mail = None
        if mail:
            contact = CandidacyContact.objects.create(candidate=candidate,
                                                      mail=mail)


def compare_lists():
    candidates_and_mails = {}
    reader = codecs.open("todos1.csv", 'r', encoding='utf-8')
    for line in reader:
        row = line.split(u',')
        area = row[2].strip()
        name = row[4].strip()
        mail = row[8].lower().strip()
        key = slugify(area + u' ' + name)
        candidates_and_mails[key] = mail
    reader = codecs.open("todos2.csv", 'r', encoding='utf-8')
    for line in reader:
        row = line.split(u',')
        area = row[0].strip()
        name = row[3].strip()
        mail = row[4].lower().strip()
        key = slugify(area + u' ' + name)
        if key in candidates_and_mails.keys():
            if candidates_and_mails[key] != mail:
                print u'el mail de ' + name + u' de ' + area + u' antes era' + candidates_and_mails[key] + u' ahora es ' + mail

def process_candidates():
    reader = codecs.open("candidates.csv", 'r', encoding='utf-8')
    counter = 0
    candidates_ids = []
    for line in reader:
        row = line.split(u',')
        area_name = row[0].title().strip()
        area = area_getter(area_name)
        if area is None:
            print u'no encontré a '+ area_name
            return
        kind_of = row[1].title().strip()
        election_name = kind_of + u' por ' + area.name
        if not Election.objects.filter(name__iexact=election_name):
            print u"no pillé a " + election_name
            # Candidate.objects.filter(id__in=candidates_ids).delete()
            return
        else:
            e = Election.objects.get(name__iexact=election_name)
        name = row[2].title().strip()
        candidate = Candidate(name=name)

        candidate.save()
        candidates_ids.append(candidate.id)
        e.candidates.add(candidate)
        print e, candidate
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
        send_candidate_username_and_password(candidate)
        counter += 1
        if not counter % 1000:
            print u'van' + str(counter)

def process_areas():
    reader = codecs.open("candidates.csv", 'r', encoding='utf-8')
    not_found_areas = []
    for line in reader:
        row = line.split(u',')
        area_name = row[0].title().strip()
        area = area_getter(area_name)
        if area is None and area_name not in not_found_areas:
            not_found_areas.append(area_name)
    print not_found_areas

def process_candidates_after():
    reader = codecs.open("candidates.csv", 'r', encoding='utf-8')
    counter = 0
    candidates_ids = []
    out_file = open("candidates2.csv", 'wb')
    candidate_writer = csv.writer(out_file, encoding='utf-8')
    for line in reader:
        row = line.split(u',')
        area_name = row[0].title().strip()
        area = area_getter(area_name)
        if area is None:
            print area_name + u' No encontrada'
            continue
        kind_of = row[1].title().strip()
        election_name = kind_of + u' por ' + area.name
        e = Election.objects.get(name__iexact=election_name)
        name = row[2].title().strip()
        if not e.candidates.filter(name=name):
            candidate_writer.writerow(row)


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


def process_twitters():
    reader = codecs.open("candidate_twitters.csv", 'r', encoding='utf-8')
    counter = 0
    candidates_ids = []
    for line in reader:
        row = line.split(u',')
        election_name = row[0].strip()
        candidate_name = row[1].strip()
        twitter = row[2].strip()
        facebook = row[3].strip()
        try:
            e = Election.objects.get(name=election_name)
        except:
            try:
                election_name = 'Alcaldes por ' + election_name
                e = Election.objects.get(name=election_name)
            except:
                print u'No pillé la elección ' + election_name
        try:
            candidate = e.candidates.get(name=candidate_name)
        except:
            print u'No pillé a ' + candidate_name
            continue
        if twitter and not candidate.twitter:
            candidate.add_contact_detail(contact_type='TWITTER', value=twitter, label=twitter)

        if facebook and not candidate.contact_details.filter(contact_type='FACEBOOK'):
            candidate.add_contact_detail(contact_type='FACEBOOK', value=facebook, label=facebook)

def export_commitments():
    total_data = []
    counter = 0
    total_data.append([u'Número', u'Comuna', u'Título', u'Url', u'Cantidad de compromisos'])
    ps = PopularProposal.objects.exclude(commitments__isnull=True)
    for p in ps:
        counter += 1
        data = [counter,
                p.area.name,
                p.title, u'http://votainteligente.cl' + p.get_absolute_url(),
                p.commitments.count()]
        for c in p.commitments.filter(candidate__elections__position='alcalde'):
            data.append(c.candidate.name)
        for c in p.commitments.filter(candidate__elections__position='concejal'):
            data.append(c.candidate.name)
        total_data.append(data)
    f = open("compromisos.csv", 'wb')
    writer = csv.writer(f, encoding='utf-8')
    writer.writerows(total_data)

def export_commitments_per_area_csv(area):
    exporter = CommitmentsExporter(area)
    f = open(area.id + '.csv', 'wb')
    w = csv.writer(f, encoding='utf-8')
    w.writerows(exporter.get_lines())

def export_commitments_for_all_areas():
    areas = [u'Arica',u'Iquique',u'Alto Hospicio',u'Antofagasta',u'Calama',u'Copiapó',u'Vallenar',u'La Serena',u'Coquimbo',u'Valparaíso',u'Viña del Mar',u'Rancagua',u'Talca',u'Curicó',u'Concepción',u'Talcahuano',u'Chillán',u'Temuco',u'Valdivia',u'Osorno',u'Puerto Varas',u'Puerto Montt',u'Coyhaique',u'Punta Arenas',u'Santiago',u'La Florida',u'Providencia',u'Maipú',u'Puente Alto',u'Las Condes',u'Vitacura',u'Ñuñoa',u'La Reina',u'Recoleta']
    as_ = Area.objects.filter(name__in=areas)
    for a in as_:
        export_commitments_per_area_csv(a)




for usuario in User.objects.exclude(proposals__isnull=True).filter(proposals__commitments__candidate__has_won=True).distinct():
    print u'Con ' + usuario.username + u',' + usuario.email
    alcaldes = Candidate.objects.filter(has_won=True, commitments__proposal__proposer=usuario).filter(elections__position='alcalde')
    if alcaldes:
        for a in alcaldes:
            print u', , ' + a.name + ', alcalde,' + a.election.area.name
    concejales = Candidate.objects.filter(has_won=True, commitments__proposal__proposer=usuario).filter(elections__position='concejal')
    if concejales:
        for con in concejales:
            print u', , ' + con.name + ', concejal,' + con.election.area.name


type_ = 'alcalde'
for usuario in User.objects.exclude(proposals__isnull=True).filter(proposals__commitments__candidate__has_won=True).distinct():
    
    alcaldes = Candidate.objects.filter(has_won=True,
                                        commitments__commited=True,
                                        commitments__proposal__proposer=usuario).filter(elections__position=type_)
    if alcaldes:
        print u'Con ' + usuario.username + u',' + usuario.email
        for a in alcaldes:
            cs = Commitment.objects.filter(candidate=a, proposal__proposer=usuario)
            commitments = ""
            for c in cs:
                commitments += ','
                commitments += '"' +c.proposal.title +'"'

            print u', , ' + a.name + ', '+ type_ + ',' + a.election.area.name + commitments


for usuario in User.objects.exclude(proposals__isnull=True).filter(proposals__commitments__candidate__has_won=True).distinct():
    concejales = Candidate.objects.filter(has_won=True,
                                          commitments__commited=True,
                                          commitments__proposal__proposer=usuario).filter(elections__position='concejal')
    if concejales:
        for con in concejales:
            cs = Commitment.objects.filter(candidate=con, proposal__proposer=usuario)
            commitments = ""
            for c in cs:
                commitments += ','
                commitments += c.proposal.title
            print u'Con ' + usuario.username + u',' + usuario.email
            print u', , ' + con.name + ', concejal,' + con.election.area.name + commitments