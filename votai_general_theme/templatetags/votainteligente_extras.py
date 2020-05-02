from django import template
from django.utils.safestring import mark_safe
from elections.models import Election, Area, Candidate
from popular_proposal.models import ProposalLike, Commitment
import json
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from popular_proposal.forms.form_texts import WHEN_CHOICES, TEXTS
from django.template.loader import render_to_string
from backend_candidate.models import is_candidate
from backend_candidate.forms import get_candidate_profile_form_class
from django.contrib.auth.forms import AuthenticationForm
from backend_citizen.forms import (UserCreationForm as RegistrationForm,
                                   GroupCreationForm)
from django.forms import Field, BoundField
from django import template
from django.template.defaultfilters import stringfilter
import re
from django.shortcuts import render
from constance import config
from organization_profiles.models import OrganizationTemplate
from popular_proposal.forms.form_texts import TOPIC_CHOICES

register = template.Library()


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
    for area in Area.public.filter(classification__in=settings.FILTERABLE_AREAS_TYPE):
        area_dict = {'slug': area.slug,
                     'name': area.name,
                     'detaillink': reverse(url, kwargs={'slug': area.slug}),
                     }
        areas.append(area_dict)
    return mark_safe(json.dumps(areas))


@register.simple_tag
def get_personal_data(**kwargs):
    candidate = kwargs.pop('candidate')
    label = kwargs.pop('personal_data')
    personal_datas = candidate.personal_datas.filter(label=label)
    if personal_datas.exists() and len(personal_datas) == 1:
        return candidate.personal_datas.get(label=label)
    return None


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
def website_imgur(value):
    if config.WEBSITE_IMGUR_CLIENT_ID:
        return config.WEBSITE_IMGUR_CLIENT_ID
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
    if config.WEBSITE_TWITTER_HASHTAG:
        return config.WEBSITE_TWITTER_HASHTAG
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


@register.filter(name='is_field')
def is_field(field):
    if isinstance(field, Field) or isinstance(field, BoundField):
        return True
    return False


@register.filter(name='support')
def support(user, proposal):
    return ProposalLike.objects.get(user=user, proposal=proposal)


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
    return fields[question].get('preview_question', question)

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
            step = ''
    return step


@register.simple_tag
def tab_text_tag(field):
    return field.field.widget.attrs.get('tab_text')


@register.filter(name='times')
def times(number):
    return range(number)


register.filter('is_candidate', is_candidate)


@register.inclusion_tag('login/basic.html')
def basic_login(url=''):
    form = AuthenticationForm()
    return {'form': form, 'url': url}


@register.inclusion_tag('login/user_register.html')
def user_register():
    form = RegistrationForm()
    return {'form': form}


@register.inclusion_tag('login/group_register.html')
def group_register():
    form = GroupCreationForm()
    return {'form': form}


@register.inclusion_tag('_user_image.html')
def user_image(user, height, width):
    size = str(width) + 'x' + str(height)
    return {'user': user,
            'height': height,
            'width': width,
            'size': size}


@register.filter(name='has_commited_with', takes_context=True)
def has_commited_with(element, proposal):
    candidate = getattr(element, 'candidate', element)
    if proposal.commitments.filter(candidate=candidate).exists():
        return True
    return False


@register.simple_tag
def get_commitment(candidacy, proposal):
    return proposal.commitments.filter(candidate=candidacy.candidate).first()


@register.simple_tag
def personal_data_label(personal_data):
    _class = get_candidate_profile_form_class()
    field = _class.base_fields.get(personal_data.label, None)
    if field is not None:
        return getattr(field, 'label', '')
    return personal_data.label


@register.simple_tag(takes_context=True)
def get_election_by_position(context, position):
    if Election.objects.filter(position=position, area=context['area']).exists():
        return Election.objects.filter(position=position, area=context['area']).first()
    else:
        return None


@register.filter(name='is_candidate_for')
def is_candidate_for(candidate, area):
    areas = []
    if candidate.elections is None:
        return False
    for election in candidate.elections.all():
        if election.area:
            areas.append(election.area.id)

    if area in Area.objects.filter(id__in=areas):
        return True
    return False


@register.filter(name='manages_this')
def manages_this(user, candidate):
    if user.is_authenticated() and user.candidacies.filter(candidate=candidate):
        return True
    return False


@register.simple_tag(name='commiters_by_election_position')
def commiters_by_election_position(proposal, position):
    return proposal.commitments.filter(candidate__elections__position=position).distinct()


@register.filter
def extract_twitter_username(value):
    if value:

        pattern = re.compile(r'((https?://)?(www\.)?twitter\.com/)?(@|#!/)?([A-Za-z0-9_]{1,15})(/([-a-z]{1,20}))?')
        result = pattern.search(value)
        if result is None:
            return ''
        return u'@' + result.groups()[4]
    else:
        return ""

@register.filter
def extract_twitter_username_without_at(value):
    if value:
        pattern = re.compile(r'((https?://)?(www\.)?twitter\.com/)?(@|#!/)?([A-Za-z0-9_]{1,15})(/([-a-z]{1,20}))?')
        result = pattern.search(value)
        if result is None:
            return ''
        return result.groups()[4]
    else:
        return ""

@register.filter
@stringfilter
def template_exists(value):
    try:
        template.loader.get_template(value)
        return True
    except template.TemplateDoesNotExist:
        return False


@register.filter(name='is_marked_area')
def is_marked_area(area):
    if area.id in config.MARKED_AREAS:
        return True
    return False


@register.simple_tag
def get_contact_detail(candidate, type_=None):
    if candidate.contact_details.filter(contact_type=type_).exists():
        return candidate.contact_details.get(contact_type=type_)


@register.simple_tag
def get_proposals_enabled():
    return config.PROPOSALS_ENABLED


@register.inclusion_tag('organizations_logos.html')
def organization_logos():
    return {'templates' : OrganizationTemplate.objects.only_with_logos()}

@register.inclusion_tag('elections/election_card.html', takes_context=True)
def display_election_card(context, election):
    return {'election': election}

@register.simple_tag(takes_context=True)
def display_proposal_card(context, proposal):
    return proposal.display_card(context)

@register.simple_tag()
def proposals_topic_choices():
    result = []
    for k,v in TOPIC_CHOICES:
        if k:
            result.append((k, v))
    return result

@register.inclusion_tag('popular_proposal_author.html')
def get_proposal_author(popular_proposal):
    link = None
    text = ''
    if popular_proposal.proposer.profile.is_organization:
        link = popular_proposal.proposer.organization_template.get_absolute_url
        text = popular_proposal.proposer.organization_template.title
    if hasattr(popular_proposal, 'gathering'):
        text = popular_proposal.gathering.name
    else:
        proposer = popular_proposal.proposer
        if not proposer.profile.is_organization:
            if proposer.get_full_name():
                text = proposer.get_full_name()
            else:
                text = proposer.username
    return {'link': link,
            'text': text
            }

@register.filter
def get_classification_from_str(classification):
    from popular_proposal.forms.form_texts import TOPIC_CHOICES_DICT
    d = TOPIC_CHOICES_DICT

    return d.get(classification, "")

@register.inclusion_tag('mails/signature.html')
def mail_signature_html():
    pass

@register.inclusion_tag('mails/signature.txt')
def mail_signature_txt():
    pass



@register.simple_tag
def committed_canididates_from(election):
    return election.candidates.filter(commitments__isnull=False)
