# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from elections.models import Election
import simplejson as json
from django.template import Template, Context


class TemplateTagsTestCase(TestCase):
	def setUp(self):
		super(TemplateTagsTestCase, self).setUp()

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