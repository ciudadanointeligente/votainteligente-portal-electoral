# coding=utf-8
from django import forms
from popular_proposal.models import ProposalTemporaryData, ProposalLike
from votainteligente.send_mails import send_mail
from django.utils.translation import ugettext as _
from django.contrib.sites.models import Site


WHEN_CHOICES = [
    ('1_month', u'1 mes después de ingresado'),
    ('6_months', u'6 Meses'),
    ('1_year', u'1 año'),
    ('2_year', u'2 años'),
    ('3_year', u'3 años'),
    ('4_year', u'4 años'),
]

TOPIC_CHOICES =(
  ('otros', 'Otros'),
  (u'Básicos',(
      (u'salud', u'Salud'),
      (u'transporte', u'Transporte'),
      (u'educacion', u'Educación'),
      (u'seguridad', u'Seguridad'),
      (u'proteccionsocial', u'Protección Social'),
      (u'vivienda', u'Vivienda'),
      )),
  (u'Oportunidades',(
      (u'trabajo', u'Trabajo'),
      (u'emprendimiento', u'Emprendimiento'),
      (u'capacitacion', u'Capacitación'),
      (u'beneficiosbienestar', u'Beneficios/bienestar'),
      )),
  (u'Espacios comunales',(
      (u'areasverdes', u'Áreas verdes'),
      (u'territoriobarrio', u'Territorio/barrio'),
      (u'obras', u'Obras'),
      (u'turismoycomercio', u'Turismo y comercio'),
      )),
  (u'Mejor comuna',(
      (u'medioambiente', u'Medio Ambiente'),
      (u'culturayrecreacion', u'Cultura y recreación'),
      (u'deporte', u'Deporte'),
      (u'servicios', u'Servicios'),
      )),
  (u'Democracia',(
      (u'transparencia', u'Transparencia'),
      (u'participacionciudadana', u'Participación ciudadana'),
      (u'genero', u'Género'),
      (u'pueblosindigenas', u'Pueblos indígenas'),
      (u'diversidadsexual', u'Diversidad sexual'),
      (u'terceraedad', u'Tercera edad'),
      ))
)

class ProposalFormBase(forms.Form):
    problem = forms.CharField(label=_(u'Según la óptica de tu organización, describe un problema de la comuna que \
quieran solucionar. (2 líneas)'),
                              help_text=_(u'Ej: Poca participación en el Plan Regulador, Falta de transparencia en \
el trabajo de la municipalidad, Pocos puntos de reciclaje, etc.'),
                              max_length=512)
    solution = forms.CharField(label=_(u'¿Qué debería hacer la municipalidad para solucionar el problema? (3 líneas)'),
                               help_text=_(u'Ejemplo: "Crear una ciclovia que circunvale Valdivia", \
"Que se publiquen todos los concejos municipales en el sitio web del municipio".'),
                               max_length=256,
                              )
    solution_at_the_end = forms.CharField(label=u"Describe la medida específica que quieren solicitar a los candidatos. ¿Qué avance concreto esperan que se logre durante el periodo del alcalde (4 años)?",
                                          help_text=_(u'Ejemplo: "Aumentar en un 20% la cantidad de ciclovías en la ciudad"'),
                                          required=False)
    when = forms.ChoiceField(choices=WHEN_CHOICES, label=_(u'¿En qué plazo debería estar implementada esta solución?'))
    title = forms.CharField(label=_(u'Resumen'),
                            help_text=_(u"Escribe un título que nos permita describir tu propuesta\
ciudadana. Ej: 50% más de ciclovías para la comuna"),
                              max_length=256,)
    clasification = forms.ChoiceField(choices=TOPIC_CHOICES, label=_(u'¿En qué área clasificarías tu propuesta?'))
    allies = forms.CharField(label=_(u'¿Quiénes son tus posibles aliados?'),
                             max_length=256)
    organization = forms.CharField(label=_(u'¿Estás haciendo esta propuesta a nombre de una organización? Escribe su nombre acá:'),
                                   required=False)


class ProposalForm(ProposalFormBase):
    def __init__(self, *args, **kwargs):
        self.proposer = kwargs.pop('proposer')
        self.area = kwargs.pop('area')
        super(ProposalForm, self).__init__(*args, **kwargs)

    def save(self):
        return ProposalTemporaryData.objects.create(proposer=self.proposer,
                                                    area=self.area,
                                                    data=self.cleaned_data)


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
        send_mail(mail_context, 'popular_proposal_moderation', to=[self.temporary_data.proposer.email])
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

