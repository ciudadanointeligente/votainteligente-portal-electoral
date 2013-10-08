from django import template

register = template.Library()

from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from elections.models import Election
import simplejson as json
from django.conf import settings

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