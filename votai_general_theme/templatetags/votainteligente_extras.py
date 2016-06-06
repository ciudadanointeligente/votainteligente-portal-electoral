from django import template

register = template.Library()

from django.utils.safestring import mark_safe
from elections.models import Election
import json
from django.conf import settings
from django.contrib.sites.models import Site
from popolo.models import Area
from django.core.urlresolvers import reverse
from popular_proposal.forms.form_texts import WHEN_CHOICES, TEXTS
from django.template.loader import render_to_string


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
            'detaillink': election.get_absolute_url(),
            'tags': tags
        }
        expected_elections.append(election_dict)
    return mark_safe(json.dumps(expected_elections))


@register.simple_tag
def areas_json(url='area'):
    areas = []
    for area in Area.objects.all():
        area_dict = {'slug': area.id,
                     'name': area.name,
                     'detaillink': reverse(url, kwargs={'slug': area.id}),
                     }
        areas.append(area_dict)
    return mark_safe(json.dumps(areas))


@register.filter
def val_navbars(section):
    if section in settings.NAV_BAR:
        return True


@register.simple_tag
def title(election, name):
    return election + ' - ' + name


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
    twitter = context["candidate"].twitter
    if twitter:
        context["twitter"] = twitter
        return context
    context["twitter"] = None
    return context
register.inclusion_tag('elections/twitter/no_candidator_answer.html',
    takes_context=True)(no_ha_respondido_twitter_button)


def follow_on_twitter(context):
    twitter = context["candidate"].twitter
    if twitter:
        context["twitter"] = twitter
        return context
    context["twitter"] = None
    return context
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


def twitter_on_ranking(context, btn_text, popup_text):
    twitter = context["candidate"].twitter
    if twitter:
        return {
            'twitter': twitter,
            'candidate': context['candidate'],
            'btn_text': btn_text,
            'popup_text': popup_text
            }
    return {
        'twitter': None,
        'candidate': context['candidate'],
        'btn_text': btn_text,
        'popup_text': popup_text
        }

register.inclusion_tag('elections/twitter/ranking_twitter.html', takes_context=True)(twitter_on_ranking)


@register.filter
#website general settings
def website_twitter(value):
    if value in settings.WEBSITE_TWITTER:
        return settings.WEBSITE_TWITTER[value]
    return ''


@register.inclusion_tag('elections/taken_position.html')
def get_taken_position_for(topic, candidate, only_text=False):
    return {'taken_position': topic.get_taken_position_for(candidate),
            'only_text': only_text,
            'candidate': candidate
            }


@register.inclusion_tag('elections/candidates/personal_data_detail.html')
def display_personal_data(item):
    return {
        'label': item[0],
        'display': item[1]['display'],
        'value': item[1]['value']
    }


@register.inclusion_tag('elections/soulmate_explanation.html')
def display_explanation(explanation, election):
    return {
        'explanation_container': explanation
    }


@register.filter(name='likes')
def likes(user, proposal):
    if user in proposal.likers.all():
        return True
    return False


@register.filter(name='popular_proposal_when')
def popular_proposal_when(when):
    for item in WHEN_CHOICES:
        if item[0] == when:
            return item[1]
    return when

@register.filter(name='popular_proposal_question')
def popular_proposal_question(question):
    fields = TEXTS
    if question not in fields.keys():
        return question
    return fields[question].get('label', question)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.inclusion_tag('popular_proposal/_extra_info.html')
def get_questions_and_descriptions(temporary_proposal):
    return {
        'texts': TEXTS,
        'data': temporary_proposal.data
    }


@register.simple_tag
def hide_tag(field):
    aux="hide"
    if field.field.widget.attrs.get('visible'):
        aux=""
    return aux

@register.simple_tag
def long_text_tag(field):
    long_text = field.field.widget.attrs.get('long_text')
    step = ''
    if long_text:
        try:
            step = render_to_string('popular_proposal/steps/' + long_text)
        except Exception, e:
            print e
            step = ''
    return step


@register.simple_tag
def tab_text_tag(field):
    return field.field.widget.attrs.get('tab_text')
