# coding=utf-8
from django import forms
from popular_proposal.models import (PopularProposal
                                     )
from elections.models import Area, QuestionCategory, Election
from django.conf import settings
from formtools.wizard.views import SessionWizardView
from medianaranja2.proposals_getter import ProposalsGetter, ProposalsGetterByReadingGroup
from django.shortcuts import render
from medianaranja2.calculator import Calculator
from constance import config
from organization_profiles.models import OrganizationTemplate
from django.views.generic.base import TemplateView
from django.core.cache import cache
from django.utils.safestring import mark_safe
from django.db.models import Q
from medianaranja2.grouped_multiple_choice_fields import GroupedModelMultiChoiceField
from medianaranja2.candidate_proposals_matrix_generator import OrganizationMatrixCreator
from django.forms import ModelForm



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

area_field = forms.ModelChoiceField(label=u"¿En qué comuna votas?",
                                    help_text=u"Si quieres conocer con qué candidatura al Congreso eres más compatible, elige la comuna en la que votas. Si sólo te interesa tu media naranja presidencial, elige “no aplica”.",
                                    empty_label=u"NO APLICA",
                                    required=False,
                                    queryset=Area.objects.filter(classification__in=settings.FILTERABLE_AREAS_TYPE).order_by('name'))

categories_field = CategoryMultipleChoiceField(label=u"De estos temas, ¿cuáles son los que te parecen más importantes para el país?",
                                               queryset=QuestionCategory.objects.none(),
                                               widget=forms.CheckboxSelectMultiple(),)
class SetupForm(forms.Form):

    def __init__(self, *args, **kwargs):
        should_use_categories = kwargs.pop('should_use_categories', True)
        super(SetupForm, self).__init__(*args, **kwargs)
        if should_use_categories:
            self.fields['categories'] = categories_field

        if settings.SECOND_ROUND_ELECTION is None:
            self.fields['area'] = area_field
            if 'categories' in self.fields:
                self.fields['categories'].queryset = QuestionCategory.objects.all().order_by('-name')
        else:
            self.election = Election.objects.get(slug=settings.SECOND_ROUND_ELECTION)
            if 'categories' in self.fields:
                self.fields['categories'].queryset = self.election.categories.order_by('-name')

    def clean(self):
        cleaned_data = super(SetupForm, self).clean()
        if settings.SECOND_ROUND_ELECTION is not None:
            cleaned_data['element_selector'] = Election.objects.get(slug=settings.SECOND_ROUND_ELECTION)
        else:
            if cleaned_data['area'] is None:
                cleaned_data['area'] = Area.objects.get(id=config.DEFAULT_AREA)

        if 'area' in cleaned_data.keys():
            cleaned_data['element_selector'] = cleaned_data['area']

        return cleaned_data


class QuestionsForm(forms.Form):
    topic_fields = []
    def __init__(self, *args, **kwargs):
        categories = kwargs.pop('categories')
        super(QuestionsForm, self).__init__(*args, **kwargs)
        self.set_fields(categories)


    def set_fields(self, categories):
        self.categories = categories
        for category in self.categories:
            for topic in category.topics.order_by('id'):
                field = PositionChoiceField(label=topic.label,
                                            empty_label=None,
                                            queryset=topic.positions,
                                            widget=forms.RadioSelect
                                            )
                self.fields[topic.slug] = field
                self.topic_fields.append(topic.slug)

    def clean(self):
        cleaned_data = super(QuestionsForm, self).clean()
        r = {"positions": []}
        for topic in cleaned_data:
            if topic in self.topic_fields:
                r['positions'].append(cleaned_data[topic])
            else:
                r[topic] = cleaned_data[topic]

        return r

class ProposalsForm(forms.Form):
    proposals = ProposalModelMultipleChoiceField(queryset=PopularProposal.objects.none(),
                                                 group_by_field='clasification',
                                                 widget=forms.CheckboxSelectMultiple(attrs={'class': 'proposal_option'}))

    def __init__(self, *args, **kwargs):
        self.proposals = kwargs.pop('proposals')
        element_selector = kwargs.pop('element_selector')
        super(ProposalsForm, self).__init__(*args, **kwargs)
        proposals_qs_cache_key = 'proposals_qs_' + str(element_selector.id)
        if cache.get(proposals_qs_cache_key) is not None:
            self.fields['proposals'].queryset = cache.get(proposals_qs_cache_key)
            return
        self.proposals = self.proposals[:config.MEDIA_NARANJA_MAX_NUM_PR]
        qs = PopularProposal.objects.filter(id__in=[p.id for p in self.proposals]).order_by('clasification')
        cache.set(proposals_qs_cache_key, qs)
        self.fields['proposals'].queryset = qs


class MediaNaranjaException(Exception):
    pass


class MediaNaranjaWizardFormBase(SessionWizardView):
    template_name = 'medianaranja2/paso_default.html'
    done_template_name = 'medianaranja2/resultado.html'
    calculator_class = Calculator
    calculator_extra_kwargs = {}

    def get_proposal_class(self):
        if config.ESTRATEGIA_SELECCION_PROPUESTAS == 'reading_group':
            return ProposalsGetterByReadingGroup
        return ProposalsGetter

    def get_proposal_getter_kwargs(self):
        return {}

    def get_proposal_getter(self):
        return self.get_proposal_class()(**self.get_proposal_getter_kwargs())

    def get_organization_templates(self, proposals):
        if settings.RECOMMENDED_ORGS_FROM_CACHE:
            c = OrganizationMatrixCreator()
            return c.get_organizations(proposals)
        else:
            is_creator_of_this_proposals_filter = Q(organization__proposals__in=proposals)
            is_liker_of_this_proposals = Q(organization__likes__proposal__in=proposals)
            organization_templates = OrganizationTemplate.objects.filter(is_creator_of_this_proposals_filter|is_liker_of_this_proposals).distinct()
            return organization_templates

    def done(self, form_list, **kwargs):
        cleaned_data = self.get_all_cleaned_data()
        results = []
        has_parent = True
        element_selector = self.get_element_selector_from_cleaned_data(cleaned_data)
        elections = self.get_proposal_getter().get_elections(element_selector)
        proposals = cleaned_data.get('proposals', [])
        positions = cleaned_data.get('positions', [])
        for election in elections:
            calculator = self.calculator_class(election, positions, proposals, **self.calculator_extra_kwargs)
            results.append(calculator.get_result())
        if settings.ORGANIZATIONS_IN_12_RESULT:
            organization_templates = self.get_organization_templates(proposals)
        else:
            organization_templates = []

        return render(self.request, self.done_template_name, {
            'results': results,
            'organizations': organization_templates
        })

    def get_template_names(self):
        return [self.templates[self.steps.current]]

    def post(self, *args, **kwargs):
        try:
            return super(MediaNaranjaWizardFormBase, self).post(*args, **kwargs)
        except MediaNaranjaException:
            self.storage.reset()
            self.storage.current_step = self.steps.first
            return self.render(self.get_form())

    def get_categories_form_kwargs(self, cleaned_data):
        return {'categories': list(cleaned_data['categories'])}

    def get_element_selector_from_cleaned_data(self, cleaned_data):
        if 'element_selector' not in cleaned_data:
            return Area.objects.get(id=config.DEFAULT_AREA)
        return cleaned_data['element_selector']

    def get_proposals_form_kwargs(self, cleaned_data):
        proposal_getter_kwargs = self.get_proposal_getter_kwargs()
        
        getter = self.get_proposal_class()(**proposal_getter_kwargs)
        element_selector = self.get_element_selector_from_cleaned_data(cleaned_data)
        proposals = getter.get_all_proposals(element_selector)
        return {'proposals': proposals, 'element_selector': element_selector}


    def get_kwargs_from_step_number(self, number, cleaned_data):
        func_name = self.steps_and_functions.get(number, None)
        if func_name is None:
            return {}
        func = getattr(self, func_name, None)
        return func(cleaned_data)

    def get_form_kwargs(self, step):
        step = int(step)
        cleaned_data = {}
        if step:
            cleaned_data = self.get_cleaned_data_for_step(str(0))
            if cleaned_data is None:
                raise MediaNaranjaException()
        return self.get_kwargs_from_step_number(step, cleaned_data)


class MediaNaranjaWizardForm(MediaNaranjaWizardFormBase):
    form_list = [SetupForm, QuestionsForm, ProposalsForm]
    steps_and_functions = {
        1: 'get_categories_form_kwargs',
        2: 'get_proposals_form_kwargs'
    }
    templates = {"0": "medianaranja2/paso_0_setup.html",
                 "1": "medianaranja2/paso_1_preguntas_y_respuestas.html",
                 "2": "medianaranja2/paso_2_proposals_list.html"}


class MediaNaranjaNoQuestionsWizardForm(MediaNaranjaWizardFormBase):
    form_list = [SetupForm, ProposalsForm]
    steps_and_functions = {
        1: 'get_proposals_form_kwargs'
    }
    templates = {"0": "medianaranja2/paso_0_setup.html",
                 "1": "medianaranja2/paso_2_proposals_list.html"}

    def get_form_kwargs(self, step):
        kwargs = super(MediaNaranjaNoQuestionsWizardForm, self).get_form_kwargs(step)
        if step == '0':
            kwargs['should_use_categories'] = False
        return kwargs


class MediaNaranjaOnlyProposals(MediaNaranjaWizardFormBase):
    form_list = [ProposalsForm, ]
    steps_and_functions = {
        0: 'get_proposals_form_kwargs'
    }
    templates = {"0": "medianaranja2/paso_2_proposals_list.html"}


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

from medianaranja2.models import SharedResult

class ShareForm(ModelForm):
    object_id = forms.CharField()
    percentage = forms.FloatField(required=False)

    class Meta:
        model = SharedResult
        fields = ['object_id', 'percentage']

    def __init__(self, *args, **kwargs):
        self.content_type = kwargs.pop('content_type')
        super(ShareForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(ShareForm, self).save(commit=False)
        instance.content_type = self.content_type
        instance.data = self.cleaned_data
        if commit:
            instance.save()
        return instance
