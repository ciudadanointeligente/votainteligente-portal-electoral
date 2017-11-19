# coding=utf-8
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "votainteligente.settings")
django.setup()
from urllib2 import urlopen, Request, HTTPError
import json
import re
from elections.models import Candidate, Election, Area
import roman
import sys


def set_has_won(candidate):
    c.has_won=True
    c.save()

def only_print_name(candidate):
    print candidate

class GetterAbstract(object):
    def __init__(self, commit=False):
        self.commit = commit

    def set_winner(self, name):
        try:
            c= Candidate.objects.get(name__icontains=name)
            if self.commit:
                set_has_won(c)
            else:
                only_print_name(c)
        except:
            print u'nopilléa'+unicode(name)

    def extract_candidate_and_name(self, dictionary):
        name = dictionary.get('name')
        regex = r'^\d+\.\s*'
        name = re.sub(regex,'', name)
        name = re.sub(r'\s\s', ' ', name)
        electo = dictionary.get('electo')
        if electo:
            self.set_winner(name)
                

    def extract_data_candidates_from(self, d):
        if isinstance(d, list):
            for c in d:
                if c['sd'] is None:
                    self.extract_candidate_and_name({'name': c['a'], 'electo':c['f']})
                else:
                    self.extract_data_candidates_from(c['sd'])

    def get_json_for_distrito(self, n):
        url = self.url % n
        headers = {'Accept':'application/json',
                   'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
        
        request = Request(url, headers=headers)
        try:
            json_content = urlopen(request).read()
            data = json.loads(json_content)['data']
            for d in data:
                self.extract_data_candidates_from(d['sd'])
        except HTTPError:
            pass


class DistritoGetter(GetterAbstract):
    url = 'http://www.servelelecciones.cl/data/elecciones_diputados/computo/distritos/60%s.json' 

class CircunscriptionGetter(GetterAbstract):
    url = 'http://www.servelelecciones.cl/data/elecciones_senadores/computo/circ_senatorial/50%s.json'

class ElectionGetter(object):
    def __init__(self, klass, election_qs, remover):
        self.klass = klass
        self.election_qs = election_qs
        self.remover = remover
        self.commit = commit

    def do_it(self, commit=False):
        for e in self.election_qs:
            n = self.remover(e.name)
            if len(n) == 1:
                n = '0' + n
            getter = self.klass(commit=commit)
            getter.get_json_for_distrito(n)

if __name__ == "__main__":
    commit = False
    try:
        if sys.argv[1] == '--commit':
            commit = True
    except IndexError:
        pass
    def remover1(name):
        return name.replace('Diputados del Distrito ', '')
    qs = Election.objects.filter(name__icontains='Diputados del Distrito ')
    e = ElectionGetter(DistritoGetter, qs, remover1)
    e.do_it(commit=commit)

    def remover2(name):
        r = name.replace(u" Circunscripción Senatorial", "")
        i = roman.fromRoman(r)
        return str(i)
    qs = Area.objects.filter(name__icontains=u"Circunscripción Senatorial")
    e = ElectionGetter(CircunscriptionGetter, qs, remover2)
    e.do_it()
    e1 = ElectionGetter(CircunscriptionGetter, "Distrito",'Diputados del Distrito ')
    e.do_it(commit=commit)
