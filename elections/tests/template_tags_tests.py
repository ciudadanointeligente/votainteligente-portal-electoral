# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from elections.models import Election
import simplejson as json
from django.template import Template, Context
from django.conf import settings
from django.contrib.sites.models import Site


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

			election_dict = {
			'name': election.name,
			'slug': election.slug,
			'detaillink':election.get_absolute_url(),
			'tags':tags
			}
			expected_elections.append(election_dict)

		
		template = Template("{% load votainteligente_extras %}{% elections_json %}")
		context = Context({})

		self.assertEqual(template.render(context), json.dumps(expected_elections))

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