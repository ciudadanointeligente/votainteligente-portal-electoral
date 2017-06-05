# coding=utf-8
from django import forms
from popular_proposal.models import (ProposalTemporaryData,
                                     ProposalLike,
                                     PopularProposal,
                                     ProposalCreationMixin,
                                     Commitment)
from votainteligente.send_mails import send_mail
from django.utils.translation import ugettext as _
from django.contrib.sites.models import Site
from .form_texts import TEXTS, TOPIC_CHOICES, WHEN_CHOICES
from elections.models import Area
from collections import OrderedDict
from votainteligente.send_mails import send_mails_to_staff
from constance import config


class TextsFormMixin():

    def add_texts_to_fields(self):
        for field in self.fields:
            if field in TEXTS.keys():
                texts = TEXTS[field]
                if 'label' in texts.keys() and texts['label']:
                    self.fields[field].label = texts['label']
                if 'help_text' in texts.keys() and texts['help_text']:
                    self.fields[field].help_text = texts['help_text']
                if 'placeholder' in texts.keys() and texts['placeholder']:
                    self.fields[field].widget.attrs[
                        'placeholder'] = texts['placeholder']
                if 'long_text' in texts.keys() and texts['long_text']:
                    self.fields[field].widget.attrs[
                        'long_text'] = texts['long_text']
                if 'step' in texts.keys() and texts['step']:
                    self.fields[field].widget.attrs['tab_text'] = texts['step']


def get_user_organizations_choicefield(user=None):
    if user is None or not user.is_authenticated():
        return None

    if user.enrollments.all():
        choices = [('', 'Lo haré a nombre personal')]
        for enrollment in user.enrollments.all():
            choice = (enrollment.organization.id, enrollment.organization.name)
            choices.append(choice)
        label = _(u'¿Esta promesa es a nombre de un grupo ciudadano?')
        return forms.ChoiceField(choices=choices,
                                 label=label)
    return None

wizard_forms_fields = [
    {
        'template': 'popular_proposal/wizard/paso1.html',
        'explation_template': "popular_proposal/steps/paso1.html",
        'fields': OrderedDict([(
            'clasification', forms.ChoiceField(choices=TOPIC_CHOICES,
                                               widget=forms.Select())
        ),
            ('problem', forms.CharField(max_length=1024,
                                        widget=forms.Textarea()
                                        ))
        ])
    },
    {
        'template': 'popular_proposal/wizard/form_step.html',
        'explation_template': "popular_proposal/steps/paso2.html",
        'fields': OrderedDict([(
            'causes', forms.CharField(max_length=256,
                                      widget=forms.Textarea()
                                      )

        )])
    },
    {
        'template': 'popular_proposal/wizard/paso3.html',
        'explation_template': "popular_proposal/steps/paso3.html",
        'fields': OrderedDict([(

            'solution', forms.CharField(max_length=2048,
                                        widget=forms.Textarea(),
                                        )
        )])
    },
    {
        'template': 'popular_proposal/wizard/form_step.html',
        'explation_template': "popular_proposal/steps/paso4.html",
        'fields': OrderedDict([(
            'solution_at_the_end', forms.CharField(widget=forms.Textarea(),
                                                   required=False)

        ),
            ('when', forms.ChoiceField(widget=forms.Select(),
                                       choices=WHEN_CHOICES))
        ])
    },
    {
        'template': 'popular_proposal/wizard/paso5.html',
        'explation_template': "popular_proposal/steps/paso5.html",
        'fields': OrderedDict([
            ('title', forms.CharField(max_length=256,
                                      widget=forms.TextInput())),
            ('join_advocacy_url', forms.URLField(max_length=256, required=False)),
            ('organization', get_user_organizations_choicefield),
            ('terms_and_conditions', forms.BooleanField(
                error_messages={'required':
                                _(u'Debes aceptar nuestros Términos y Condiciones')}
            )
            )
        ])
    }
]


def get_form_list(wizard_forms_fields=wizard_forms_fields, **kwargs):
    form_list = []
    counter = 0
    for step in wizard_forms_fields:
        counter += 1
        fields_dict = OrderedDict()
        for field in step['fields']:
            tha_field = step['fields'][field]
            if hasattr(tha_field, '__call__'):
                executed_field = tha_field.__call__(**kwargs)
                if executed_field is not None:
                    fields_dict[field] = executed_field
            else:
                fields_dict[field] = tha_field

        def __init__(self, *args, **kwargs):
            self.is_staff = kwargs.pop('is_staff', False)
            super(forms.Form, self).__init__(*args, **kwargs)
            self.add_texts_to_fields()
        cls_attrs = {"__init__": __init__,
                     "explanation_template": step['explation_template'],
                     "template": step['template']}
        form_class = type('Step%d' % (counter),
                          (forms.Form, TextsFormMixin, object), cls_attrs)
        form_class.base_fields = fields_dict
        form_list.append(form_class)
    return form_list


class ProposalFormBase(forms.Form, TextsFormMixin):
    def set_fields(self):
        fields = OrderedDict()
        for steps in wizard_forms_fields:
            for field_name in steps['fields']:
                field = steps['fields'][field_name]
                if hasattr(field, '__call__'):
                    kwargs = {'user': self.proposer}
                    field = field.__call__(**kwargs)
                    if field is None:
                        continue
                fields[field_name] = field
        return fields

    def __init__(self, *args, **kwargs):
        self.proposer = kwargs.pop('proposer', None)
        super(ProposalFormBase, self).__init__(*args, **kwargs)
        self.fields.update(self.set_fields())
        self.add_texts_to_fields()


class CreateProposalMixin(ProposalCreationMixin):
    def save(self):
        kwargs = self.determine_kwargs(proposer=self.proposer,
                                       area=self.area,
                                       data=self.cleaned_data,
                                       model_class=self.model_class)
        t_data = self.model_class.objects.create(**kwargs)
        t_data.notify_new()
        return t_data


class ProposalForm(ProposalFormBase, CreateProposalMixin):
    model_class = ProposalTemporaryData
    def __init__(self, *args, **kwargs):
        self.area = kwargs.pop('area')
        super(ProposalForm, self).__init__(*args, **kwargs)


class UpdateProposalForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        return super(UpdateProposalForm, self).__init__(*args, **kwargs)

    class Meta:
        model = PopularProposal
        fields = ['background', 'contact_details', 'image', 'document']
        labels = {'background': _(u'Más antecedentes sobre tu propuesta.'),
                  'image': _(u'¿Tienes alguna imagen para compartir?'),
                  'document': _(u'¿Tienes algún documento para complementar tu propuesta?'),
                  'contact_details': _(u'¿Cómo te puede contactar un candidato?')
                  }
        help_texts = {'background': _(u'Ejemplo: Durante el año 2011, existió una iniciativa de otra comunidad que no llegó a buen puerto.'),
                      'contact_details': _(u'Ejemplo: Tu teléfono o el lugar donde eres ubicable y en qué horario.')}


class CommentsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.temporary_data = kwargs.pop('temporary_data')
        self.moderator = kwargs.pop('moderator')
        super(CommentsForm, self).__init__(*args, **kwargs)
        for field in self.temporary_data.comments.keys():
            try:
                help_text = _(u'La ciudadana dijo: %s') % self.temporary_data.data.get(field, u'')
            except:
                help_text = _(u'Ocurrió un problema sacando los datos')
            comments = self.temporary_data.comments[field]
            if comments:
                help_text += _(u' <b>Y tus comentarios fueron: %s </b>') % comments
            self.fields[field] = forms.CharField(required=False, help_text=help_text)

    def save(self, *args, **kwargs):
        for field_key in self.cleaned_data.keys():
            self.temporary_data.comments[field_key] = self.cleaned_data[field_key]
        self.temporary_data.status = ProposalTemporaryData.Statuses.InTheirSide
        self.temporary_data.save()
        comments = {}
        for key in self.temporary_data.data.keys():
            if self.temporary_data.comments[key]:
                comments[key] = {
                    'original': self.temporary_data.data[key],
                    'comments': self.temporary_data.comments[key]
                }

        site = Site.objects.get_current()
        mail_context = {
            'area': self.temporary_data.area,
            'temporary_data': self.temporary_data,
            'moderator': self.moderator,
            'comments': comments,
            'site': site,

        }
        send_mail(mail_context, 'popular_proposal_moderation',
                  to=[self.temporary_data.proposer.email])
        return self.temporary_data


class RejectionForm(forms.Form):
    reason = forms.CharField()

    def __init__(self, *args, **kwargs):
        self.temporary_data = kwargs.pop('temporary_data')
        self.moderator = kwargs.pop('moderator')
        super(RejectionForm, self).__init__(*args, **kwargs)

    def reject(self):
        self.temporary_data.reject(self.cleaned_data['reason'])


FIELDS_TO_BE_AVOIDED = ['terms_and_conditions', ]

class ProposalTemporaryDataUpdateForm(ProposalFormBase):
    overall_comments = forms.CharField(required=False,
                                       label=_(u'Comentarios sobre tu revisón'),
                                       widget=forms.Textarea())


    def __init__(self, *args, **kwargs):
        self.proposer = kwargs.pop('proposer')
        self.temporary_data = kwargs.pop('temporary_data')
        field_order = self.get_fields_order(self.temporary_data)
        super(ProposalTemporaryDataUpdateForm, self).__init__(*args, **kwargs)
        self.order_fields(field_order)
        for field_to_be_avoided in FIELDS_TO_BE_AVOIDED:
            self.fields.pop(field_to_be_avoided)
        self.initial = self.temporary_data.data
        commented_fields = []
        for comment_key in self.temporary_data.comments.keys():
            comment = self.temporary_data.comments[comment_key]
            if comment:
                commented_fields.append(comment_key)
                self.fields[comment_key].help_text += _(' <b>Creemos que: %s </b>') % (comment)

    def get_fields_order(self, temporary_data):
        commented_fields = []
        fields_at_the_end = ProposalTemporaryDataUpdateForm.base_fields
        fields = self.set_fields()

        for comment_key in temporary_data.comments.keys():
            comment = temporary_data.comments[comment_key]
            if comment:
                commented_fields.append(comment_key)
        keyOrder = commented_fields
        for field in fields:
            if field not in commented_fields and field not in fields_at_the_end:
                keyOrder.append(field)
        for field in fields_at_the_end:
            keyOrder.append(field)
        return keyOrder

    def order_fields(self, field_order):
        if hasattr(self, 'keyOrder'):
            field_order = self.keyOrder
        super(ProposalTemporaryDataUpdateForm, self).order_fields(field_order)

    def save(self):
        self.overall_comments = self.cleaned_data.pop('overall_comments')
        self.temporary_data.data = self.cleaned_data
        self.temporary_data.overall_comments = self.overall_comments
        self.temporary_data.status = ProposalTemporaryData.Statuses.InOurSide
        self.temporary_data.save()
        send_mails_to_staff({'temporary_data': self.temporary_data}, 'notify_staff_new_proposal_update')
        return self.temporary_data

    def get_overall_comments(self):
        return self.cleaned_data.get('overall_comments', '')


class SubscriptionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.proposal = kwargs.pop('proposal')
        super(SubscriptionForm, self).__init__(*args, **kwargs)

    def subscribe(self):

        like, created = ProposalLike.objects.get_or_create(user=self.user,
                                                           proposal=self.proposal)
        return like


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


class ProposalFilterFormBase(forms.Form):
    clasification = forms.ChoiceField(TOPIC_CHOICES, required=False)

    def __init__(self, *args, **kwargs):
        super(ProposalFilterFormBase, self).__init__(*args, **kwargs)

    def _set_initial(self):
        for field_name, field in self.fields.items():
            if field_name in self.initial.keys():
                self.fields[field_name].initial = self.initial[field_name]


class ProposalFilterForm(ProposalFilterFormBase):
    area = forms.ChoiceField(required=False)

    def __init__(self, *args, **kwargs):
        super(ProposalFilterForm, self).__init__(*args, **kwargs)
        self.fields['area'].choices = [('', _(u'Selecciona una comuna'))]
        self.fields['area'].choices += [(a.id, a.name) for a in Area.public.all()]
        self._set_initial()


class ProposalAreaFilterForm(ProposalFilterFormBase):

    def __init__(self, area, *args, **kwargs):
        self.area = area
        super(ProposalAreaFilterForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name in self.initial.keys():
                self.fields[field_name].initial = self.initial[field_name]


class ProposalTemporaryDataModelForm(forms.ModelForm, ProposalFormBase):
    class Meta:
        model = ProposalTemporaryData
        exclude = ['organization', 'data']

    def __init__(self, *args, **kwargs):
        super(ProposalTemporaryDataModelForm, self).__init__(*args, **kwargs)
        for key in self.fields.keys():
            if key in self.instance.data.keys():
                self.fields[key].initial = self.instance.data[key]

    def save(self, *args, **kwargs):
        instance = super(ProposalTemporaryDataModelForm, self).save(*args, **kwargs)
        for key in instance.data.keys():
            instance.data[key] = self.cleaned_data[key]
        instance.save()
        return instance


class CandidateCommitmentFormBase(forms.Form):
    terms_and_conditions = forms.BooleanField(initial=False,
                                              required=True,
                                              label=_(u'Términos y Condiciones'))

    commited = True

    def __init__(self, candidate, proposal, *args, **kwargs):
        super(CandidateCommitmentFormBase, self).__init__(*args, **kwargs)
        self.candidate = candidate
        self.proposal = proposal

    def save(self):
        commitment = Commitment.objects.create(proposal=self.proposal,
                                               candidate=self.candidate,
                                               commited=self.commited)
        return commitment

    def clean(self):
        cleaned_data = super(CandidateCommitmentFormBase, self).clean()
        if self.candidate.election:
            if self.candidate.election.area != self.proposal.area:
                raise forms.ValidationError(_(u'El candidato no pertenece al area'))
        else:
            raise forms.ValidationError(_(u'El candidato no pertenece al area'))
        return cleaned_data


class CandidateCommitmentForm(CandidateCommitmentFormBase):
    commited = True


class CandidateNotCommitingForm(CandidateCommitmentFormBase):
    detail = forms.CharField(required=False,
                             widget=forms.Textarea(),
                             label=_(u'Explica tus razones para NO comprometerte con esta propuesta ciudadana'))
    commited = False

    def save(self):
        commitment = super(CandidateNotCommitingForm, self).save()
        commitment.detail = self.cleaned_data['detail']
        commitment.save()
        return commitment
