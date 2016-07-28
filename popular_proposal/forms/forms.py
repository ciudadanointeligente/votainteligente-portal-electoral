# coding=utf-8
from django import forms
from popular_proposal.models import (ProposalTemporaryData,
                                     ProposalLike,
                                     PopularProposal)
from votainteligente.send_mails import send_mail
from django.utils.translation import ugettext as _
from django.contrib.sites.models import Site
from .form_texts import TEXTS, TOPIC_CHOICES, WHEN_CHOICES
from popolo.models import Area
from collections import OrderedDict


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
        'template': 'popular_proposal/wizard/form_step.html',
        'explation_template': "popular_proposal/steps/paso1.html",
        'fields': OrderedDict([
            ('problem', forms.CharField(max_length=512,
                                        widget=forms.Textarea(),
                                        ))
        ])
    },
    {
        'template': 'popular_proposal/wizard/form_step.html',
        'explation_template': "popular_proposal/steps/paso2.html",
        'fields': OrderedDict([(
            'causes', forms.CharField(max_length=256,
                                      widget=forms.Textarea(),
                                      )

        )])
    },
    {
        'template': 'popular_proposal/wizard/paso3.html',
        'explation_template': "popular_proposal/steps/paso3.html",
        'fields': OrderedDict([(
            'clasification', forms.ChoiceField(choices=TOPIC_CHOICES,
                                               widget=forms.Select())
        ), (

            'solution', forms.CharField(max_length=512,
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
            ('organization', get_user_organizations_choicefield),
            ('terms_and_conditions', forms.BooleanField(
                error_messages={'required':
                                _(u'Debes aceptar nuestros Términos y \
Condiciones')}
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
        for steps in wizard_forms_fields:
            for field_name in steps['fields']:
                field = steps['fields'][field_name]
                if hasattr(field, '__call__'):
                    kwargs = {'user': self.proposer}
                    field = field.__call__(**kwargs)
                    if field is None:
                        continue
                self.fields[field_name] = field

    def __init__(self, *args, **kwargs):
        self.proposer = kwargs.pop('proposer', None)
        super(ProposalFormBase, self).__init__(*args, **kwargs)
        self.set_fields()
        self.add_texts_to_fields()


class ProposalForm(ProposalFormBase):
    def __init__(self, *args, **kwargs):
        self.area = kwargs.pop('area')
        super(ProposalForm, self).__init__(*args, **kwargs)

    def save(self):
        t_data = ProposalTemporaryData.objects.create(proposer=self.proposer,
                                                      area=self.area,
                                                      data=self.cleaned_data)
        t_data.notify_new()
        return t_data


class UpdateProposalForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        return super(UpdateProposalForm, self).__init__(*args, **kwargs)

    class Meta:
        model = PopularProposal
        fields = ['background', 'image']


class CommentsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.temporary_data = kwargs.pop('temporary_data')
        self.moderator = kwargs.pop('moderator')
        super(CommentsForm, self).__init__(*args, **kwargs)
        for field in self.temporary_data.comments.keys():
            help_text = _(u'La ciudadana dijo: %s') % self.temporary_data.data.get(field, u'')
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


class ProposalTemporaryDataUpdateForm(ProposalFormBase):
    overall_comments = forms.CharField(required=False, label=_(u'Comentarios sobre tu revisón'))

    def __init__(self, *args, **kwargs):
        self.proposer = kwargs.pop('proposer')
        self.temporary_data = kwargs.pop('temporary_data')
        super(ProposalTemporaryDataUpdateForm, self).__init__(*args, **kwargs)
        self.initial = self.temporary_data.data
        for comment_key in self.temporary_data.comments.keys():
            comment = self.temporary_data.comments[comment_key]
            if comment:
                self.fields[comment_key].help_text += _(' <b>Commentarios: %s </b>') % (comment)

    def save(self):
        self.overall_comments = self.cleaned_data.pop('overall_comments')
        self.temporary_data.data = self.cleaned_data
        self.temporary_data.overall_comments = self.overall_comments
        self.temporary_data.status = ProposalTemporaryData.Statuses.InOurSide
        self.temporary_data.save()
        return self.temporary_data

    def get_overall_comments(self):
        return self.cleaned_data.get('overall_comments', '')


class SubscriptionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.proposal = kwargs.pop('proposal')
        super(SubscriptionForm, self).__init__(*args, **kwargs)

    def subscribe(self):
        like = ProposalLike.objects.create(user=self.user,
                                           proposal=self.proposal)
        return like


class AreaForm(forms.Form):
    area = forms.ChoiceField()
    explanation_template = "popular_proposal/steps/select_area.html"

    def __init__(self, *args, **kwargs):
        super(AreaForm, self).__init__(*args, **kwargs)
        self.fields['area'].choices = [(a.id, a.name) for a in Area.objects.all()]

    def clean(self):
        cleaned_data = super(AreaForm, self).clean()
        area = Area.objects.get(id=cleaned_data['area'])
        cleaned_data['area'] = area
        return cleaned_data


class ProposalFilterForm(forms.Form):
    area = forms.ChoiceField(required=False)
    clasification = forms.ChoiceField(TOPIC_CHOICES, required=False)

    def __init__(self, *args, **kwargs):
        super(ProposalFilterForm, self).__init__(*args, **kwargs)
        self.fields['area'].choices = [(a.id, a.name) for a in Area.objects.all()]