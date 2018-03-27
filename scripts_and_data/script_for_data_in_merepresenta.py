estados = [{"name": u"Acre", 'identifier': u"AC"},
{"name": u"Alagoas", 'identifier': u"AL"},
{"name": u"Amapá", 'identifier': u"AP"},
{"name": u"Amazonas", 'identifier': u"AM"},
{"name": u"Bahía", 'identifier': u"BA"},
{"name": u"Ceará", 'identifier': u"CE"},
{"name": u"Distrito Federal", 'identifier': u"DF"},
{"name": u"Espírito Santo", 'identifier': u"ES"},
{"name": u"Goiás", 'identifier': u"GO"},
{"name": u"Maranhão", 'identifier': u"MA"},
{"name": u"Mato Grosso", 'identifier': u"MT"},
{"name": u"Mato Grosso del Sur", 'identifier': u"MS"},
{"name": u"Minas Gerais", 'identifier': u"MG"},
{"name": u"Pará", 'identifier': u"PA"},
{"name": u"Paraíba", 'identifier': u"PB"},
{"name": u"Paraná", 'identifier': u"PR"},
{"name": u"Pernambuco", 'identifier': u"PE"},
{"name": u"Piauí", 'identifier': u"PI"},
{"name": u"Río de Janeiro", 'identifier': u"RJ"},
{"name": u"Río Grande del Norte", 'identifier': u"RN"},
{"name": u"Río Grande del Sur", 'identifier': u"RS"},
{"name": u"Rondônia", 'identifier': u"RO"},
{"name": u"Roraima", 'identifier': u"RR"},
{"name": u"Santa Catarina", 'identifier': u"SC"},
{"name": u"São Paulo", 'identifier': u"SP"},
{"name": u"Sergipe", 'identifier': u"SE"},
{"name": u"Tocantins", 'identifier': u"TO"}]




from elections.models import Area, Election
brasil = Area.objects.create(name="Brasil", identifier="BR", classification="country")
c, created = Election.objects.get_or_create(name="Presidente do Brasil", area=brasil, position=u"Presidente")
for e in estados:

    a, created = Area.objects.get_or_create(name=e['name'], identifier=e['identifier'], classification=u'state', parent=brasil)
    g, created = Election.objects.get_or_create(name="Gobernador de " + e['name'], area=a, position=u"Gobernador/a")
    d_e, created = Election.objects.get_or_create(name="Deputado Estadual", area=a, position=u'Diputada/o Estadual')
    d_f, created = Election.objects.get_or_create(name="Deputado Federal", area=a, position=u'Diputada/o Federal')
    s_f, created = Election.objects.get_or_create(name="Senado Federal", area=a, position=u'Senador/a Federal')
    elections = [c, g, d_e, d_f, s_f]
    for election in elections:
        i = 0
        while i < 3:
            i += 1
            n = u"Candidato número " + unicode(i) + u" pelo " + election.name + u" em " + election.area.name
            cand, created = Candidate.objects.get_or_create(name=n)
            election.candidates.add(cand)


ps = [{"name": u"Adoção de crianças por famílias LGBTs."},
{"name": u"Uso de banheiros por pessoas travestis e transexuais de acordo com sua identidade de gênero."},
{"name": u"Cota de 50% para mulheres no Legislativo, garantindo representatividade étnico-racial e respeito à identidade de gênero autodeclarada."},
{"name": u"Promoção de igualdade de gênero e raça e o respeito às orientações sexuais e identidades de gênero nas escolas."},
{"name": u"Cotas raciais e ações afirmativas para a população negra."},
{"name": u"Proibição da realização de cultos e o uso de símbolos religiosos em repartições públicas."},
{"name": u"Impedimento de ocupação de cargos públicos por homens que tenham agredido mulheres."},
{"name": u"Descriminalização e legalização do aborto."},
{"name": u"Criminalização da lesbofobia, homofobia, transfobia e bifobia."},
{"name": u"Desmilitarização da polícia."},
{"name": u"Desapropriação de imóveis abandonados para criação de moradias de interesse social."},
{"name": u"Licenciamento ambiental que proteja populações vulneráveis e áreas atingidas por grandes empreendimentos."},
{"name": u"Abertura de maiores espaços de participação direta da população na definição do orçamento municipal."},
{"name": u"Quebra dos contratos com empresas de mobilidade que não têm auditoria de custos e uma gestão transparente."}]



from merepresenta.models import MeRepresentaPopularProposal

site, created = Site.objects.get_or_create(name="#MeRepresenta", domain="merepresenta.127.0.0.1.xip.io:8000")
CustomSite.objects.get_or_create(site=site, urlconf="merepresenta.stand_alone_urls")
proposer, created = User.objects.get_or_create(username="merepresenta", email="merepresenta@merepresenta.org")
for p in ps:
    p = MeRepresentaPopularProposal.objects.create(proposer=proposer,
                                                   clasification='ddhh',
                                                   title=p['name'],
                                                   one_liner=p['name'],
                                                   data={}
                                                   )
    PopularProposalSite.objects.create(site=site, popular_proposal=p)



cs = Candidate.objects.filter(elections__area__name__in=[u"São Paulo", u"Río de Janeiro", u"Brasil"]).order_by("?")
ps = MeRepresentaPopularProposal.objects.order_by('?')

from random import random
for c in cs:
    for p in ps:
        r = random()
        if r > 0.5:
            MeRepresentaCommitment.objects.create(candidate=c,
                                                   proposal=p,
                                                   commited=True)



# ./manage.py dumpdata --format=yaml sites auth backend_citizen organization_profiles custom_sites popolo elections popular_proposal > merepresenta_example.yaml