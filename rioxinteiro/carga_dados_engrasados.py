from elections.models import Candidate
import uuid
from constance import config
def crea():
    a = Area.objects.get(id=config.DEFAULT_AREA)
    e = Election.objects.create(name=u"Imperador du todo mondo", area=a)
    cands = [
             {'coali': "FCI", 'email':'mfreire@cidadaniainteligente.org' , 'partido': 'vermelho', 'name': 'Malu'},
             {'coali': "FCI", 'email':'alourenco@cidadaniainteligente.org' , 'partido': 'laranjo', 'name': 'Caro'},
             {'coali': "Casa Fluminense", 'email':'contato@cidadaniainteligente.org' , 'partido': 'verde', 'name': 'Enrique'},
             {'coali': "Casa Fluminense", 'email':'contato@cidadaniainteligente.org' , 'partido': 'azul', 'name': 'victor'},
             ]
    ids_candidatos  = []
    ids_users = []
    ids_personal_data = []
    ids_propostas = []
    ids_incrementals = []

    for cand in cands:
        candidate = Candidate.objects.create(name=cand['name'])
        ids_candidatos.append(candidate.id)
        e.candidates.add(candidate)
        coali = PersonalData.objects.create(candidate=candidate, label=u'Coligação', value=cand['coali'])
        ids_personal_data.append(coali.id)
        partido = PersonalData.objects.create(candidate=candidate, label=u'Partido', value=cand['partido'])
        ids_personal_data.append(partido.id)
        user_candidate = User.objects.create_user(username=candidate.slug.lower(),
                                                  password=candidate.slug[:20] + unicode(uuid.uuid4())[:4])
        user_candidate.email = cand['email']
        user_candidate.save()
        ids_users.append(user_candidate.id)
        Candidacy.objects.create(candidate=candidate, user=user_candidate)


    u = User.objects.create_user(username='feli', password='1234')
    u.email = 'falvarez@ciudadanointeligente.org'
    u.save()
    ids_users.append(u.id)
    proposta_bicis = PopularProposal.objects.create(proposer=u,
                                                    area=a,
                                                    data={},
                                                    title=u'+ bicis',
                                                    clasification=u'education'
                                                    )
    ids_propostas.append(proposta_bicis.id)
    proposta_ciclovias = PopularProposal.objects.create(proposer=u,
                                                    area=a,
                                                    data={},
                                                    title=u'+ ciclovias',
                                                    clasification=u'education'
                                                    )
    ids_propostas.append(proposta_ciclovias.id)
    proposta_politicas_publica1 = PopularProposal.objects.create(proposer=u,
                                                    area=a,
                                                    data={},
                                                    title=u'melhores politicas publicas',
                                                    clasification=u'education'
                                                    )
    ids_propostas.append(proposta_politicas_publica1.id)
    proposta_politicas_publica2 = PopularProposal.objects.create(proposer=u,
                                                    area=a,
                                                    data={},
                                                    title=u'+ impostos',
                                                    clasification=u'education'
                                                    )
    ids_propostas.append(proposta_politicas_publica2.id)
    fci = IncrementalsCandidateFilter.objects.create(name='FCI', filter_qs={'personal_datas__value': "FCI"})
    ids_incrementals.append(fci.id)
    cf = IncrementalsCandidateFilter.objects.create(name='Casa Fluminense', filter_qs={'personal_datas__value': "Casa Fluminense"})
    ids_incrementals.append(cf.id)
    i1 = ProposalSuggestionForIncremental(incremental=fci, proposal=proposta_bicis)
    i2 = ProposalSuggestionForIncremental(incremental=fci, proposal=proposta_ciclovias)
    i3 = ProposalSuggestionForIncremental(incremental=cf, proposal=proposta_politicas_publica1)
    i4 = ProposalSuggestionForIncremental(incremental=cf, proposal=proposta_politicas_publica2)


def delete():
    Election.objects.filter(id=e.id).delete()
    Candidate.objects.filter(id__in=ids_candidatos).delete()
    PopularProposal.objects.filter(id__in=ids_propostas).delete()
    User.objects.filter(id__in=ids_users).delete()
    PersonalData.objects.filter(id__in=ids_personal_data).delete()