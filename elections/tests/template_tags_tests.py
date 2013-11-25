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
		settings.WEBSITE_METADATA = {
		    'author' : u'Fundación Ciudadano Inteligente',
		    'description' : u'Este 18 de Septiembre los chilenos elegiremos Presidente, Senadores, Diputados y Consejeros Regionales (CORE). Aqu&iacute; encontrar&aacute;s info para votar informado.',
		    'keywords' : u'elecciones, presidencia, presidenciales, senatoriales, senadores, diputados, cores, core'
		}
		settings.WEBSITE_OGP = {
		    'title' : 'Vota Inteligente',
		    'type' : 'website',
		    'url' : 'http://www.votainteligente.org/',
		    'image' : '/static/img/votai-196.png'
		}
		settings.WEBSITE_DISQUS = {
		    'visible' : True,
		    'shortname' : 'votainteligente',
		    'dev' : 1,
		}
		settings.WEBSITE_GA = {
		    'code' : 'UA-XXXXX-X'
		}
		settings.WEBSITE_GENERAL_SETTINGS = {
		    'home_title' : 'Lorem ipsum dolor sit amet, consectetur adipisicing elit.'
		}
		#imgur
		settings.WEBSITE_IMGUR = {
		    'client_id' : 'eb18642b5b220484864483b8e21386c3' #example client_id, only works with 50 pic a day
		}
		settings.WEBSITE_TWITTER = {
			'hashtags' : 'votainformado,eslaloslas'
		}

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

	def test_website_metadata(self):
		template = Template("{% load votainteligente_extras %}{{ 'author'|metadata }}")
		context = Context({})

		self.assertEqual(template.render(context), u'Fundación Ciudadano Inteligente')

	def test_website_notin_metadata(self):
		template = Template("{% load votainteligente_extras %}{{ 'tags'|metadata }}")
		context = Context({})

		self.assertEqual(template.render(context), '')

	def test_website_ogp(self):
		template = Template("{% load votainteligente_extras %}{{ 'title'|ogpdata }}")
		context = Context({})

		self.assertEqual(template.render(context), u'Vota Inteligente')

	def test_website_no_ogp(self):
		template = Template("{% load votainteligente_extras %}{{ 'sound'|ogpdata }}")
		context = Context({})

		self.assertEqual(template.render(context), u'')

	def test_website_disqus(self):
		template = Template("{% load votainteligente_extras %}{{ 'shortname'|disqus }}")
		context = Context({})

		self.assertEqual(template.render(context), u'votainteligente')

	def test_website_no_disqus_setting(self):
		template = Template("{% load votainteligente_extras %}{{ 'sound'|disqus }}")
		context = Context({})

		self.assertEqual(template.render(context), u'')

	def test_website_ga(self):
		template = Template("{% load votainteligente_extras %}{{ 'code'|ga }}")
		context = Context({})

		self.assertEqual(template.render(context), u'UA-XXXXX-X')

	def test_website_general_settings(self):
		template = Template("{% load votainteligente_extras %}{{ 'home_title'|website_gs }}")
		context = Context({})

		self.assertEqual(template.render(context), u'Lorem ipsum dolor sit amet, consectetur adipisicing elit.')

	def test_website_imgur(self):
		template = Template("{% load votainteligente_extras %}{{ 'client_id'|website_imgur }}")
		context = Context({})

		self.assertEqual(template.render(context), u'eb18642b5b220484864483b8e21386c3')

	def test_website_twitter(self):
		template = Template("{% load votainteligente_extras %}{{ 'hashtags'|website_twitter }}")
		context = Context({})

		self.assertEqual(template.render(context), u'votainformado,eslaloslas')