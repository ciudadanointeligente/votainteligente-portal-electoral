# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from elections.models import Election, Candidate
import json
from django.template import Template, Context
from django.conf import settings
from django.contrib.sites.models import Site
from django.template.loader import get_template
from candidator.models import Position, TakenPosition
from django.core.urlresolvers import reverse
from elections.models import QuestionCategory, Topic, Area, PersonalData
from django.contrib.auth.forms import AuthenticationForm
from backend_citizen.forms import (UserCreationForm as RegistrationForm,
                                   GroupCreationForm)
from django.contrib.auth.models import User
from django import forms
from backend_candidate.models import Candidacy
from popular_proposal.models import PopularProposal, Commitment
from popular_proposal.forms.form_texts import TOPIC_CHOICES
from django.test import override_settings
from django.shortcuts import render
from constance import config
from constance.test import override_config

class TemplateTagsTestCase(TestCase):
    def setUp(self):
        super(TemplateTagsTestCase, self).setUp()
        settings.NAV_BAR = ('profiles', )

    def test_bring_all_elections_with_their_tags_as_json(self):
        expected_elections = []
        for election in Election.objects.filter(searchable=True):
            tags = []
            for tag in election.tags.all():
                tags.append(tag.name)

            election_dict = {'name': election.name,
                             'slug': election.slug,
                             'detaillink': election.get_absolute_url(),
                             'tags': tags
                             }
            expected_elections.append(election_dict)

        template = Template("{% load votainteligente_extras %}{% elections_json %}")
        context = Context({})

        self.assertEqual(template.render(context), json.dumps(expected_elections))

    @override_settings(FILTERABLE_AREAS_TYPE = ['Comuna'])
    def test_areas_json_template_tag(self):
        Area.objects.all().delete()
        expected_areas = []
        chile = Area.objects.create(name="Chile", classification="Comuna")
        bolivia = Area.objects.create(name="Mar para Bolivia", classification="Comuna")
        Area.objects.create(name="Guatemala")
        for area in [chile, bolivia]:
            area_dict = {'slug': area.slug,
                         'name': area.name,
                         'detaillink': area.get_absolute_url()
                         }
            expected_areas.append(area_dict)

        template = Template("{% load votainteligente_extras %}{% areas_json %}")
        context = Context({})

        self.assertEqual(json.loads(template.render(context)), expected_areas)

    def test_get_navbar_in_setting_vars(self):

        template = Template("{% load votainteligente_extras %}{% if 'profiles'|val_navbars  %}si{% endif %}")
        context = Context({})

        self.assertEqual(template.render(context), 'si')

    def test_get_navbar_not_in_setting_var(self):
        template = Template("{% load votainteligente_extras %}{% if 'questionary'|val_navbars  %}si{% else %}no{% endif %}")
        context = Context({})

        self.assertEqual(template.render(context), 'no')

    def test_url_domain(self):
        current_domain = Site.objects.get_current()
        current_domain.domain = "votainteligente.cl"
        current_domain.save()

        template = Template("{% load votainteligente_extras %}{% url_domain %}")
        context = Context({})
        self.assertEqual(template.render(context), 'votainteligente.cl')

    def test_display_personal_data(self):
        template = Template("{% load votainteligente_extras %}{% display_personal_data item %}")
        context = Context({'item': ('nacionalidad', {'display': 'Nacionalidad',
                                                     'value': 'Es un ciudadano del mundo'})
                           })
        actual_rendered_template = template.render(context)
        self.assertIn('nacionalidad', actual_rendered_template)
        self.assertIn('Nacionalidad', actual_rendered_template)
        self.assertIn('Es un ciudadano del mundo', actual_rendered_template)

    def test_get_personal_data_from_candidate(self):
        candidate = Candidate.objects.get(id=1)
        personal_data = PersonalData.objects.create(candidate=candidate, label='Edad', value=u'31 años')
        template = Template("{% load votainteligente_extras %}{% get_personal_data candidate=candidate personal_data='Edad' as edad %}{{edad.value}}")
        context = Context({'candidate': candidate})
        rendered_template = template.render(context)
        self.assertEquals(rendered_template, personal_data.value)
        template = Template("{% load votainteligente_extras %}{% get_personal_data candidate=candidate personal_data='Non Existing' as non_existing %}{{non_existing.value}}")
        self.assertFalse(template.render(context))

    def test_get_taken_position_by_candidate(self):
        topic = Topic.objects.create(
            label=u"Should marijuana be legalized?",
            description=u"This is a description of the topic of marijuana")

        position = Position.objects.create(
            topic=topic,
            label=u"Yes",
            description=u"Yes, means that it is considered a good thing for marijuana to be legalized"
        )
        candidate = Candidate.objects.create(name=u"Felipe")
        taken_position = TakenPosition.objects.create(
            topic=topic,
            position=position,
            person=candidate,
        )
        template = Template("{% load votainteligente_extras %}{% get_taken_position_for topic candidate %}")
        context = Context({'topic': topic,
                           'candidate': candidate,
                           })
        actual_rendered_template = template.render(context)
        template_str = get_template('elections/taken_position.html')
        expected_template = template_str.render({'taken_position': taken_position,
                                                 'candidate': candidate,
                                                 'only_text': False})
        self.assertTrue(expected_template)
        self.assertEqual(actual_rendered_template, expected_template)
        template_str = get_template('elections/taken_position.html')
        expected_template = template_str.render({'taken_position': taken_position, 'only_text': True})
        template = Template("{% load votainteligente_extras %}{% get_taken_position_for topic candidate only_text=True %}")
        actual_rendered_template = template.render(context)
        self.assertEqual(expected_template, actual_rendered_template)

    def test_filter_times(self):
        template = Template("{% load votainteligente_extras %}{% for i in 3|times %}hola{% endfor %}")
        context = Context({})

        self.assertEqual(template.render(context), u'holaholahola')


class LoginFormsTemplateTags(TestCase):
    def setUp(self):
        super(LoginFormsTemplateTags, self).setUp()

    def test_get_login_basic_form(self):
        template_str = get_template('login/basic.html')
        url = reverse('backend_citizen:index')
        form = AuthenticationForm()
        rendered_template = template_str.render({'url': url, 'form': form})
        template = Template("{% load votainteligente_extras %}{% basic_login url=url %}")
        self.assertEqual(template.render(Context({'url': url})),
                         rendered_template)

    def test_get_register_form(self):
        template_str = get_template('login/user_register.html')
        form = RegistrationForm()
        rendered_template = template_str.render({'form': form})
        template = Template("{% load votainteligente_extras %}{% user_register %}")
        self.assertEqual(template.render(Context({})),
                         rendered_template)

    def test_get_group_register_form(self):
        template_str = get_template('login/group_register.html')
        form = GroupCreationForm()
        rendered_template = template_str.render({'form': form})
        template = Template("{% load votainteligente_extras %}{% group_register %}")
        self.assertEqual(template.render(Context({})),
                         rendered_template)

    def test_variable_is_field(self):
        template = Template("{% load votainteligente_extras %}{% if field|is_field  %}si{% else %}no{% endif %}")
        field = forms.CharField(required=False, label='Busca tu comuna')
        self.assertEqual(template.render(Context({'field': field})), 'si')
        data = {'username': 'fierita',
                'password1': 'feroz',
                'password2': 'feroz',
                'email': 'fiera@feroz.cl'}
        form = RegistrationForm(data=data)
        field = form.fields['username']
        self.assertEqual(template.render(Context({'field': field})), 'si')
        self.assertEqual(template.render(Context({'field': 'esto es un string'})), 'no')

    def test_user_image(self):
        u = User.objects.get(username='feli')
        template_str = get_template('_user_image.html')
        rendered_template = template_str.render({'user': u,
                                                 'size': '100x120',
                                                 'height': 120,
                                                 'width': 100})
        template = Template("{% load votainteligente_extras %}{% user_image user=user height=120 width=100 %}")
        self.assertEqual(template.render(Context({'user': u, 'height': 120, 'width': 100})),
                         rendered_template)

    def test_get_election_by_position(self):
        argentina = Area.objects.create(name=u'Argentina')
        election = Election.objects.create(
            name='the name',
            slug='the-slug',
            description='this is a description',
            extra_info_title=u'ver más',
            area=argentina,
            position='alcalde',
            extra_info_content=u'Más Información')

        template = Template("{% load votainteligente_extras %}{% get_election_by_position 'alcalde' as election %}{{election.name}}")
        context = Context({'area': argentina})
        rendered_template = template.render(context)
        self.assertEquals(election.name, rendered_template)
        template2 = Template("{% load votainteligente_extras %}{% get_election_by_position 'concejal' as election %}{{election.name}}")
        self.assertFalse(template2.render(context))
        chile = Area.objects.create(name=u'Chile')
        election.area = chile
        election.save()
        template3 = Template("{% load votainteligente_extras %}{% get_election_by_position 'alcalde' as election %}{{election.name}}")
        self.assertFalse(template3.render(context))

        # Two elections with the same position doesn't raise error
        election.area = argentina
        election.save()
        election = Election.objects.create(
            name='the name2',
            slug='the-slug',
            description='this is a description',
            extra_info_title=u'ver más',
            area=argentina,
            position='alcalde',
            extra_info_content=u'Más Información')
        self.assertTrue(template.render(context))

    def test_candidate_has_commited(self):
        # Mar para Bolivia
        chile = Area.objects.create(name="Chile")
        u = User.objects.get(username='feli')
        data = {'clasification': 'educacion',
                'title': u'Mar para Bolivia',
                'problem': u'Los bolivianos no tienen mar y son bacanes',
                'solution': u'Que le den mar soberano a Bolivia',
                'when': u'1_year',
                'causes': u'El egoismo chileno.'
                }
        popular_proposal = PopularProposal.objects.create(proposer=u,
                                                          area=chile,
                                                          data=data,
                                                          title=u'This is a title',
                                                          clasification=u'education'
                                                          )
        candidate = Candidate.objects.get(pk=1)
        candidacy = Candidacy.objects.create(user=u,
                                             candidate=candidate
                                             )
        commitment = Commitment.objects.create(candidate=candidate,
                                               proposal=popular_proposal,
                                               commited=True)
        template = Template("{% load votainteligente_extras %}{% if candidacy|has_commited_with:proposal %}si{% else %}no{% endif %}")

        self.assertEqual(template.render(Context({'candidacy': candidacy,
                                                  'proposal': popular_proposal})), 'si')
        template = Template("{% load votainteligente_extras %}{% if candidate|has_commited_with:proposal %}si{% else %}no{% endif %}")
        self.assertEqual(template.render(Context({'candidate': candidate,
                                                  'proposal': popular_proposal})), 'si')
        template2 = Template("{% load votainteligente_extras %}{% get_commitment candidacy proposal as commitment %}{{commitment.proposal.title}}")
        self.assertEqual(template2.render(Context({'candidacy': candidacy,
                                                  'proposal': popular_proposal})), popular_proposal.title)
        commitment.delete()
        self.assertEqual(template.render(Context({'candidacy': candidacy,
                                                  'proposal': popular_proposal})), 'no')


    def test_get_commited_candidates_for_election(self):
        chile = Area.objects.create(name="Chile")
        u = User.objects.get(username='feli')
        data = {'clasification': 'educacion',
                'title': u'Mar para Bolivia',
                'problem': u'Los bolivianos no tienen mar y son bacanes',
                'solution': u'Que le den mar soberano a Bolivia',
                'when': u'1_year',
                'causes': u'El egoismo chileno.'
                }
        popular_proposal = PopularProposal.objects.create(proposer=u,
                                                          area=chile,
                                                          data=data,
                                                          title=u'This is a title',
                                                          clasification=u'education'
                                                          )
        candidate = Candidate.objects.get(pk=1)
        election = candidate.election
        commitment = Commitment.objects.create(candidate=candidate,
                                               proposal=popular_proposal,
                                               commited=True)
        template = Template("{% load votainteligente_extras %}{% committed_canididates_from election as candidates %}{% for candidate in candidates %}{{candidate.name}}{% endfor %}")
        self.assertEqual(template.render(Context({'election': election})), candidate.name)

    def test_is_candidate_for_this_area(self):
        candidate = Candidate.objects.get(pk=1)
        template = Template("{% load votainteligente_extras %}{% if candidate|is_candidate_for:area %}si{% else %}no{% endif %}")
        context = Context({'candidate': candidate,
                           'area': candidate.election.area})
        self.assertEquals(template.render(context), 'si')
        chile = Area.objects.create(name="Chile")
        context = Context({'candidate': candidate,
                           'area': chile})
        self.assertEquals(template.render(context), 'no')

    def test_is_user_manager_for_this_candidate(self):
        u = User.objects.get(username='feli')
        candidate = Candidate.objects.get(pk=1)
        Candidacy.objects.create(user=u,
                                 candidate=candidate
                                 )
        template = Template("{% load votainteligente_extras %}{% if user|manages_this:candidate %}si{% else %}no{% endif %}")
        context = Context({'user': u,
                           'candidate': candidate})
        self.assertEquals(template.render(context), 'si')
        u = User.objects.get(username='fiera')
        context = Context({'user': u,
                           'candidate': candidate})
        self.assertEquals(template.render(context), 'no')

    def test_get_amount_of_commiters_per_election_position(self):
        u = User.objects.get(username='fiera')
        feli = User.objects.get(username='feli')
        chile = Area.objects.create(name='Chile')

        candidate = Candidate.objects.get(pk=1)
        election = Election.objects.get(id=1)
        election.position = 'alcalde'
        election.area = chile
        election.save()
        candidate2 = Candidate.objects.get(pk=2)
        election.candidates.remove(candidate2)
        election2 = Election.objects.get(id=2)
        election2.position = 'concejal'
        election2.area = chile
        election2.save()
        candidate3 = Candidate.objects.get(pk=3)
        election2.candidates.remove(candidate)
        election.candidates.add(candidate)
        election2.candidates.remove(candidate2)
        election2.candidates.remove(candidate3)
        election2.candidates.add(candidate2)
        election2.candidates.add(candidate3)

        data = {'clasification': 'educacion',
                'title': u'Mar para Bolivia',
                'problem': u'Los bolivianos no tienen mar y son bacanes',
                'solution': u'Que le den mar soberano a Bolivia',
                'when': u'1_year',
                'causes': u'El egoismo chileno.'
                }
        proposal = PopularProposal.objects.create(proposer=u,
                                                  area=chile,
                                                  data=data,
                                                  title=u'This is a title',
                                                  clasification=u'education'
                                                  )
        proposal_without_area = PopularProposal.objects.create(proposer=u,
                                                               data=data,
                                                               title=u'This is a title',
                                                               clasification=u'education'
                                                               )
        Commitment.objects.create(candidate=candidate,
                                  proposal=proposal,
                                  commited=True)

        Commitment.objects.create(candidate=candidate2,
                                  proposal=proposal,
                                  commited=True)
        Commitment.objects.create(candidate=candidate3,
                                  proposal=proposal,
                                  commited=True)

        # Officially 1 alcaldes have said I commit and 2 concejales
        template = Template("{% load votainteligente_extras %}{% commiters_by_election_position proposal 'alcalde' as commiters %}{{commiters.count}}")
        context = Context({'proposal': proposal})
        self.assertEquals(template.render(context), '1')

        template = Template("{% load votainteligente_extras %}{% commiters_by_election_position proposal 'concejal' as commiters %}{{commiters.count}}")
        context = Context({'proposal': proposal})
        self.assertEquals(template.render(context), '2')
        Commitment.objects.create(candidate=candidate3,
                                  proposal=proposal_without_area,
                                  commited=True)
        template = Template("{% load votainteligente_extras %}{% commiters_by_election_position proposal 'concejal' as commiters %}{{commiters.count}}")
        context = Context({'proposal': proposal_without_area})
        self.assertEquals(template.render(context), '1')

    def test_twitter_parser(self):
        asserts = [{'entered': 'https://twitter.com/fiera',
                    'expected': '@fiera'},
                   {'entered': '@fiera',
                    'expected': '@fiera'},
                   {'entered': 'twitter.com/fiera',
                    'expected': '@fiera'},
                   {'entered': 'http://www.twitter.com/#!/fiera',
                    'expected': '@fiera'},
                   {'entered': 'https://twitter.com/fiera',
                    'expected': '@fiera'},
                   {'entered': 'http://www.twitter.com/#!/fiera/following',
                    'expected': '@fiera'},
                   {'entered': 'http://twitter.com/#!/fiera/lists/memberships',
                    'expected': '@fiera'}
                   ]
        for a in asserts:
            template = Template("{% load votainteligente_extras %}{{ twitter|extract_twitter_username }}")
            rendered = template.render(Context({'twitter': a['entered']}))
            self.assertEquals(rendered,
                              a['expected'],
                              u'Intentando con ' + a['entered'] + u' obtengo ' + rendered + u' en lugar de ' + a['expected'])

    def test_twitter_parser_without_at(self):
        asserts = [{'entered': 'https://twitter.com/fiera',
                    'expected': 'fiera'},
                   {'entered': '@fiera',
                    'expected': 'fiera'},
                   {'entered': 'twitter.com/fiera',
                    'expected': 'fiera'},
                   {'entered': 'http://www.twitter.com/#!/fiera',
                    'expected': 'fiera'},
                   {'entered': 'https://twitter.com/fiera',
                    'expected': 'fiera'},
                   {'entered': 'http://www.twitter.com/#!/fiera/following',
                    'expected': 'fiera'},
                   {'entered': 'http://twitter.com/#!/fiera/lists/memberships',
                    'expected': 'fiera'}
                   ]
        for a in asserts:
            template = Template("{% load votainteligente_extras %}{{ twitter|extract_twitter_username_without_at }}")
            rendered = template.render(Context({'twitter': a['entered']}))
            self.assertEquals(rendered,
                              a['expected'],
                              u'Intentando con ' + a['entered'] + u' obtengo ' + rendered + u' en lugar de ' + a['expected'])

    @override_config(MARKED_AREAS=['argentina',])
    def test_marked_areas(self):
        argentina = Area.objects.create(name=u'Argentina', slug='argentina')
        chile = Area.objects.create(name=u'Chile', slug='chile')
        template = Template("{% load votainteligente_extras %}{% if area|is_marked_area %}si{% else %}no{% endif %}")

        context = Context({'area': argentina})
        self.assertEquals(template.render(context), 'si')
        context = Context({'area': chile})
        self.assertEquals(template.render(context), 'no')

    def test_get_contact_detail(self):
        candidate = Candidate.objects.get(id=1)
        candidate2 = Candidate.objects.get(id=2)
        candidate.add_contact_detail(contact_type='CPLT', value='perrito', label='perrito')
        template = Template("{% load votainteligente_extras %}{% get_contact_detail candidate type_='CPLT' as link%}{{link.value}}")
        context = Context({'candidate': candidate})
        self.assertEquals(template.render(context), 'perrito')
        context = Context({'candidate': candidate2})
        self.assertEquals(template.render(context), '')

    @override_config(PROPOSALS_ENABLED=False)
    def test_candidates_not_commiting(self):
        template = Template("{% load votainteligente_extras %}{% get_proposals_enabled as proposals_enabled %}{% if proposals_enabled  %}si{% else %}no{% endif %}")
        context = Context({})
        self.assertEquals(template.render(context), 'no')

    @override_config(PROPOSALS_ENABLED=True)
    def test_candidates_commiting_if_enabled(self):
        template = Template("{% load votainteligente_extras %}{% get_proposals_enabled as proposals_enabled %}{% if proposals_enabled  %}si{% else %}no{% endif %}")
        context = Context({})
        self.assertEquals(template.render(context), 'si')

    def test_get_election_tag(self):
        election = Election.objects.get(id=2)
        template = Template("{% load votainteligente_extras %}{% display_election_card election %}")
        context = Context({'election': election})

        self.assertEquals(template.render(context), election.card(context))

    def test_proposal_card(self):
        u = User.objects.get(username='feli')
        data = {'clasification': 'educacion',
                'title': u'Mar para Bolivia',
                'problem': u'Los bolivianos no tienen mar y son bacanes',
                'solution': u'Que le den mar soberano a Bolivia',
                'when': u'1_year',
                'causes': u'El egoismo chileno.'
                }
        popular_proposal = PopularProposal.objects.create(proposer=u,
                                                          data=data,
                                                          title=u'This is a title',
                                                          clasification=u'education'
                                                          )
        template = Template("{% load votainteligente_extras %}{% display_proposal_card popular_proposal %}")
        context = {'popular_proposal': popular_proposal}
        expected = template.render(Context(context))
        actual = popular_proposal.display_card(Context(context))
        self.assertEquals(expected, actual)

        kids_proposal = PopularProposal.objects.create(proposer=u,
                                                    data=data,
                                                    title=u'This is a title',
                                                    clasification=u'education'
                                                    )
        context = Context({'popular_proposal': kids_proposal})
        self.assertEquals(template.render(context), kids_proposal.display_card(context))

    def test_get_proposer_name(self):
        u = User.objects.get(username='feli')
        data = {'clasification': 'educacion',
                'title': u'Mar para Bolivia',
                'problem': u'Los bolivianos no tienen mar y son bacanes',
                'solution': u'Que le den mar soberano a Bolivia',
                'when': u'1_year',
                'causes': u'El egoismo chileno.'
                }
        popular_proposal = PopularProposal.objects.create(proposer=u,
                                                          data=data,
                                                          title=u'This is a title',
                                                          clasification=u'education'
                                                          )
        template = Template("{% load votainteligente_extras %}{% get_proposal_author popular_proposal %}")
        template_str = get_template('popular_proposal_author.html')
        context = {'link': None,
                   'text': 'feli'}
        expected_template = template_str.render(context)
        self.assertEquals(expected_template, template.render(Context({'popular_proposal': popular_proposal})))
        o = User.objects.create(username='organization')
        o.profile.is_organization = True
        o.profile.save()
        o.organization_template.title = "Esta es una org"
        o.organization_template.save()
        popular_proposal.proposer = o
        popular_proposal.save()
        context = {'link': o.organization_template.get_absolute_url(),
                   'text': o.organization_template.title }
        expected_template = template_str.render(context)
        self.assertEquals(expected_template, template.render(Context({'popular_proposal': popular_proposal})))

    def test_proposal_TOPIC_CHOICES(self):
        expected_r = ""
        for t in TOPIC_CHOICES:
            if t[0]:
                expected_r += u"<" +  t[0] + u"|" + t[1] + u">"
        template = Template("{% load votainteligente_extras %}{% proposals_topic_choices as classifications %}{% for k,v in classifications %}<{{k}}|{{v}}>{% endfor %}")
        context = Context({})

        self.assertEquals(template.render(context), expected_r)
