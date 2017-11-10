# coding=utf-8
from django import forms
from popular_proposal.models import (PopularProposal
                                     )
from elections.models import Area, QuestionCategory
from django.conf import settings
from formtools.wizard.views import SessionWizardView
from medianaranja2.proposals_getter import ProposalsGetter
from django.shortcuts import render
from medianaranja2.calculator import Calculator
from constance import config
from organization_profiles.models import OrganizationTemplate
from django.views.generic.base import TemplateView
from django.core.cache import cache
from django.utils.safestring import mark_safe
from django.db.models import Q
from medianaranja2.grouped_multiple_choice_fields import GroupedModelMultiChoiceField


class CategoryMultipleChoiceField(forms.ModelMultipleChoiceField):
    template_name = 'django/forms/widgets/checkbox_select.html'
    option_template_name = 'django/forms/widgets/checkbox_option.html'

    def label_from_instance(self, obj):
        return obj.name

class PositionChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.label


class ProposalModelMultipleChoiceField(GroupedModelMultiChoiceField):

    def label_from_instance(self, obj):
        return mark_safe( obj.get_one_liner() )


class SetupForm(forms.Form):
    area = forms.ModelChoiceField(label=u"¿En qué comuna votas?",
                                  help_text=u"Si quieres conocer con qué candidatura al Congreso eres más compatible, elige la comuna en la que votas. Si sólo te interesa tu media naranja presidencial, elige “no aplica”.",
                                  empty_label=u"NO APLICA",
                                  required=False,
                                  queryset=Area.objects.filter(classification__in=settings.FILTERABLE_AREAS_TYPE).order_by('name'))
    categories = CategoryMultipleChoiceField(label=u"De estos temas, ¿cuáles son los que te parecen más importantes para el país?",
                                             queryset=QuestionCategory.objects.all().order_by('name'),
                                             widget=forms.CheckboxSelectMultiple(),)

    def clean(self):
        cleaned_data = super(SetupForm, self).clean()
        if cleaned_data['area'] is None:
            cleaned_data['area'] = Area.objects.get(id=config.DEFAULT_AREA)
        return cleaned_data


class QuestionsForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.categories = kwargs.pop('categories')
        super(QuestionsForm, self).__init__(*args, **kwargs)
        for category in self.categories:
            for topic in category.topics.order_by('id'):
                field = PositionChoiceField(label=topic.label,
                                            empty_label=None,
                                            queryset=topic.positions,
                                            widget=forms.RadioSelect
                                            )
                self.fields[topic.slug] = field

    def clean(self):
        cleaned_data = super(QuestionsForm, self).clean()
        r = {"positions": []}
        for topic in cleaned_data:
            r['positions'].append(cleaned_data[topic])

        return r

class ProposalsForm(forms.Form):
    proposals = ProposalModelMultipleChoiceField(queryset=PopularProposal.objects.none(),
                                                 group_by_field='clasification',
                                                 widget=forms.CheckboxSelectMultiple(attrs={'class': 'proposal_option'}))

    def __init__(self, *args, **kwargs):
        self.proposals = kwargs.pop('proposals')
        area = kwargs.pop('area')
        super(ProposalsForm, self).__init__(*args, **kwargs)
        proposals_qs_cache_key = 'proposals_qs_' + area.id
        if cache.get(proposals_qs_cache_key) is not None:
            self.fields['proposals'].queryset = cache.get(proposals_qs_cache_key)
            return
        self.proposals = self.proposals[:config.MEDIA_NARANJA_MAX_NUM_PR]
        qs = PopularProposal.objects.filter(id__in=[p.id for p in self.proposals]).order_by('clasification')
        cache.set(proposals_qs_cache_key, qs)
        self.fields['proposals'].queryset = qs

FORMS = [SetupForm, QuestionsForm, ProposalsForm]
TEMPLATES = {"0": "medianaranja2/paso_0_setup.html",
             "1": "medianaranja2/paso_1_preguntas_y_respuestas.html",
             "2": "medianaranja2/paso_2_proposals_list.html"}


class MediaNaranjaException(Exception):
    pass


class MediaNaranjaWizardForm(SessionWizardView):
    form_list = FORMS
    template_name = 'medianaranja2/paso_default.html'

    def done(self, form_list, **kwargs):
        cleaned_data = self.get_all_cleaned_data()
        results = []
        has_parent = True
        area = cleaned_data['area']
        while has_parent:
            if area.elections.all():
                for election in area.elections.all():
                    calculator = Calculator(election, cleaned_data['positions'], cleaned_data['proposals'])
                    results.append(calculator.get_result())
            if not area.parent:
                has_parent = False
            else:
                area = area.parent
        is_creator_of_this_proposals_filter = Q(organization__proposals__in=cleaned_data['proposals'])
        is_liker_of_this_proposals = Q(organization__likes__proposal__in=cleaned_data['proposals'])
        organization_templates = OrganizationTemplate.objects.filter(is_creator_of_this_proposals_filter|is_liker_of_this_proposals).distinct()
        return render(self.request, 'medianaranja2/resultado.html', {
            'results': results,
            'organizations': organization_templates
        })

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def post(self, *args, **kwargs):
        try:
            return super(MediaNaranjaWizardForm, self).post(*args, **kwargs)
        except MediaNaranjaException:
            self.storage.reset()
            self.storage.current_step = self.steps.first
            return self.render(self.get_form())

    def get_form_kwargs(self, step):
        step = int(step)
        cleaned_data = {}
        if step:
            cleaned_data = self.get_cleaned_data_for_step(str(0))
            if cleaned_data is None:
                raise MediaNaranjaException()
        if step == 1:
            return {'categories': list(cleaned_data['categories'])}
        if step == 2:
            getter = ProposalsGetter()
            proposals = getter.get_all_proposals(cleaned_data['area'])
            return {'proposals': proposals, 'area': cleaned_data['area']}

        return {}


class MediaNaranjaResultONLYFORDEBUG(TemplateView):# pragma: no cover
    template_name = 'medianaranja2/resultado.html'

    def get_context_data(self, **kwargs):
        context = super(MediaNaranjaResultONLYFORDEBUG, self).get_context_data(**kwargs)
        from elections.models import Candidate, Election
        from organization_profiles.models import OrganizationTemplate
        templates = OrganizationTemplate.objects.all()[:3]
        context['organizations'] = templates
        e1 = Election.objects.exclude(candidates__isnull=True)[0]
        context['results'] =  [
                    {'election': e1,
                       'candidates': [{'value': 2.0, 'candidate': e1.candidates.all()[0]},
                      {'value': 1.0, 'candidate': e1.candidates.all()[1]},
                      {'value': 0.5, 'candidate': e1.candidates.all()[2]}]}]
        return context