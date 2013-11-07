from django import template

register = template.Library()

from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from elections.models import Election
import simplejson as json
from django.conf import settings
from django.contrib.sites.models import Site
import re

@register.simple_tag
def elections_json():
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
	return mark_safe(json.dumps(expected_elections))

@register.filter
def val_navbars(section):
	if section in settings.NAV_BAR:
		return True

@register.simple_tag
def title(election, name):	
	return election + ' - ' + name;

@register.simple_tag
def url_domain():
    return Site.objects.get_current().domain

@register.filter
def metadata(meta):
	if meta in settings.WEBSITE_METADATA:
		return settings.WEBSITE_METADATA[meta]
	return ''

@register.filter
def ogpdata(ogp):
	if ogp in settings.WEBSITE_OGP:
		return settings.WEBSITE_OGP[ogp]
	return ''

@register.filter
def disqus(disqus):
	if disqus in settings.WEBSITE_DISQUS:
		return settings.WEBSITE_DISQUS[disqus]
	return ''

@register.filter
def ga(value):
	if value in settings.WEBSITE_GA:
		return settings.WEBSITE_GA[value]
	return ''

def no_ha_respondido_twitter_button(context):
	twitter = context["candidate"].relation.twitter
	if twitter:
		return {
			'twitter':twitter,
			'candidate':context['candidate']
			}
	return {
		'twitter':None,
		'candidate':context['candidate']
		}
register.inclusion_tag('elections/twitter/no_candidator_answer.html', 
	takes_context=True)(no_ha_respondido_twitter_button)


def follow_on_twitter(context):
	twitter = context["candidate"].relation.twitter
	if twitter:
		return {
			'twitter':twitter,
			'candidate':context['candidate']
			}
	return {
		'twitter':None,
		'candidate':context['candidate']
		}
register.inclusion_tag('elections/twitter/follow_the_conversation.html', 
	takes_context=True)(follow_on_twitter)

@register.filter
#website general settings
def website_gs(value):
	if value in settings.WEBSITE_GENERAL_SETTINGS:
		return settings.WEBSITE_GENERAL_SETTINGS[value]
	return ''

@register.filter
#website general settings
def website_imgur(value):
	if value in settings.WEBSITE_IMGUR:
		return settings.WEBSITE_IMGUR[value]
	return ''
