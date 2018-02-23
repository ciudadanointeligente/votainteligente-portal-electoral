# coding=utf-8
from django import forms
from elections.models import Area
from popular_proposal.forms.forms import ProposalForm, UpdateProposalForm, AuthorityCommitmentForm
from constance import config
from django.conf import settings
from django.utils.translation import ugettext as _


class ProposalWithAreaForm(ProposalForm):
    def __init__(self, *args, **kwargs):
        self.area = kwargs.pop('area')
        self.original_kwargs['area'] = 'area'
        super(ProposalWithAreaForm, self).__init__(*args, **kwargs)


class AreaForm(forms.Form):
    area = forms.ChoiceField()
    explanation_template = "popular_proposal/steps/select_area.html"
    template = 'popular_proposal/wizard/select_area.html'

    def __init__(self, *args, **kwargs):
        is_staff = kwargs.pop('is_staff', False)
        super(AreaForm, self).__init__(*args, **kwargs)
        area_qs = Area.public.all()
        if is_staff:
            area_qs = Area.objects.all()
        self.fields['area'].choices = [(a.id, a.name) for a in area_qs]
        if config.DEFAULT_AREA:
            self.initial['area'] = config.DEFAULT_AREA

    def clean(self):
        cleaned_data = super(AreaForm, self).clean()
        if 'area' not in cleaned_data:
            return cleaned_data
        area = Area.objects.get(id=cleaned_data['area'])
        cleaned_data['area'] = area
        return cleaned_data


def get_possible_generating_areas():
    area_qs = Area.public.all()
    if settings.POSSIBLE_GENERATING_AREAS_FILTER:
        area_qs = area_qs.filter(classification=settings.POSSIBLE_GENERATING_AREAS_FILTER)
    return area_qs


def get_possible_generating_areas_choices():
    area_qs = get_possible_generating_areas()
    choices = [('', _(u'No aplica'))]
    choices += [(a.id, a.name) for a in area_qs]
    return choices


class UpdateProposalForm(UpdateProposalForm):
    def __init__(self, *args, **kwargs):
        super(UpdateProposalForm, self).__init__(*args, **kwargs)
        self.fields['generated_at'].choices = get_possible_generating_areas_choices()


def wizard_forms_field_modifier(wizard_forms_fields):
    generated_at = {'generated_at': forms.ModelChoiceField(required=False,
                                                     queryset=get_possible_generating_areas(),
                                                     empty_label="No aplica")}
    wizard_forms_fields[-1]['fields'].update(generated_at)
    return wizard_forms_fields

class VotaInteligenteAuthorityCommitmentFormBase(AuthorityCommitmentForm):
    def clean(self):
        cleaned_data = super(VotaInteligenteAuthorityCommitmentFormBase, self).clean()
        if not self.authority.election.candidates_can_commit_everywhere:
            if self.authority.election:
                if self.authority.election.area != self.proposal.area:
                    raise forms.ValidationError(_(u'El candidato no pertenece al area'))
            else:
                raise forms.ValidationError(_(u'El candidato no pertenece al area'))
        return cleaned_data

class VotaInteligenteAuthorityCommitmentForm(VotaInteligenteAuthorityCommitmentFormBase):
    commited = True

class VotaInteligenteAuthorityNotCommitingForm(VotaInteligenteAuthorityCommitmentFormBase):
    commited = False