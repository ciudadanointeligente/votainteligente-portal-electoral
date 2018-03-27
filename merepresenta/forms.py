# coding=utf-8
from django import forms
from medianaranja2.forms import ProposalModelMultipleChoiceField, MediaNaranjaWizardForm
from popular_proposal.models import PopularProposal
from django.core.cache import cache
from django.conf import settings
from elections.models import Area
from django.contrib.sites.models import Site
from medianaranja2.proposals_getter import ByOnlySiteProposalGetter
from merepresenta.models import MeRepresentaPopularProposal
from django.utils.safestring import mark_safe


class MeRepresentaProposalModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    template_name = 'merepresenta/checkbox_select.html'
    option_template_name = 'merepresenta/checkbox_option.html'

    def label_from_instance(self, obj):
        return mark_safe( obj.get_one_liner() )

class MeRepresentaProposalsForm(forms.Form):
    proposals = MeRepresentaProposalModelMultipleChoiceField(queryset=MeRepresentaPopularProposal.objects.none(),
                                                 widget=forms.CheckboxSelectMultiple(attrs={'class': 'proposal_option'}))
    area = forms.ModelChoiceField(label=u"Em que estado você vota?",
                                    help_text=u"Se você quiser saber com que candidatura ao Congresso você é mais compatível, escolha o estado em que você vota. Se você está interessado apenas em sua mídia presidencial, escolha 'não se aplica'.",
                                    empty_label=u"Não se aplica",
                                    required=False,
                                    queryset=Area.objects.filter(classification__in=settings.FILTERABLE_AREAS_TYPE).order_by('name'))

    def __init__(self, *args, **kwargs):
        self.proposals = kwargs.pop('proposals')
        super(MeRepresentaProposalsForm, self).__init__(*args, **kwargs)
        proposals_qs_cache_key = 'merepresenta_proposals_qs'
        if cache.get(proposals_qs_cache_key) is not None:
            self.fields['proposals'].queryset = cache.get(proposals_qs_cache_key)
            return
        qs = MeRepresentaPopularProposal.objects.filter(id__in=[p.id for p in self.proposals]).order_by('clasification')
        cache.set(proposals_qs_cache_key, qs)
        self.fields['proposals'].queryset = qs



class MeRepresentaMeiaLaranjaWizardForm(MediaNaranjaWizardForm):
    template_name = 'merepresenta/perguntas.html'
    done_template_name = 'merepresenta/resultado.html'
    form_list = [MeRepresentaProposalsForm]
    steps_and_functions = {
        0: 'get_proposals_form_kwargs'
    }

    def get_template_names(self):
        return self.template_name

    def get_proposal_class(self):
        return ByOnlySiteProposalGetter

    def get_proposal_getter_kwargs(self):
        site = Site.objects.get(id=settings.MEREPRESENTA_SITE_ID)
        return {'site': site, 'proposal_class': MeRepresentaPopularProposal}

    def get_element_selector_from_cleaned_data(self, cleaned_data):
        return cleaned_data.get('area', None)

    def get_proposals_form_kwargs(self, cleaned_data):
        proposal_getter_kwargs = self.get_proposal_getter_kwargs()
        getter = self.get_proposal_class()(**proposal_getter_kwargs)

        proposals = getter.get_all_proposals(self.get_element_selector_from_cleaned_data(cleaned_data))
        return {'proposals': proposals}