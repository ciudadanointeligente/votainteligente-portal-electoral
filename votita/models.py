# coding=utf-8
from __future__ import unicode_literals
from django.db import models
from django.template.loader import get_template
from picklefield.fields import PickledObjectField
from popular_proposal.models import PopularProposal
from multiselectfield import MultiSelectField
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from elections.models import Area
from taggit.managers import TaggableManager
from django.core.urlresolvers import reverse


PRESIDENTS_FEATURES = (
 (u'Habilidades intelectuales', (
   ('inteligente', 'Inteligente'),
   ('creativo', 'Creativo/a'),
   ('objetivo', 'Objetivo'),
   ('con_iniciativa', 'Con Iniciativa'),
   ('profesional', 'Profesional'),
   ('culto', 'Culto/a'),
   ('bilingue', 'Bilingüe'),
  )
 ),
 ('Valores', (
   ('responsable', 'Responsable'),
   ('transparente', 'Transparente'),
   ('honesto', 'Honesto/a'),
   ('equitativo', 'Equitativo/a'),
   ('justo', 'Justo/a'),
   ('comprometido', 'Comprometido/a'),
  )
 ),
 ('Habilidades personales', (
   ('integrador', 'Integrador/a'),
   ('motivador', 'Motivador/a'),
   ('abierto', 'Abierto/a a escuchar'),
   ('accesible', 'Accesible'),
   ('empatico', 'Empático/a'),
   ('confiable', 'Confiable'),
  )
 ),
 ('Habilidades de rol', (
   ('lider', 'Lider'),
   ('administrador', 'Buen Administrador/a'),
   ('negociante', 'Buen Negociante'),
   ('comunicador', 'Buen Comunicador/a'),
   ('influyente', 'Influyente'),
   ('eficiente', 'Eficiente'),
   ('experiencia', 'Con experiencia'),
  )
 ),
)
class KidsGathering(models.Model):
    proposer = models.ForeignKey(User, related_name="kids_proposals")
    name = models.CharField(max_length=512,
                            verbose_name="Grupo de participantes")
    stats_data = PickledObjectField()
    presidents_features = TaggableManager(verbose_name="")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='votita/images/',
                              max_length=512,
                              null=True,
                              blank=True,
                              verbose_name="")
    generated_at = models.ForeignKey(Area,
                                     null=True,
                                     blank=True)
    comments = models.TextField(verbose_name=u"¿Tienes algún comentario sobre la actividad?",
                                help_text=u"¿Cómo podemos empoderar mejor a nuestros niños?",
                                blank=True,
                                default=u"")

    class Meta:
        verbose_name = _(u'Encuentro')
        verbose_name_plural = _(u"Encuentros")

    @property
    def presidents_features_str(self):
        result = []
        all_features = {}
        for pf in PRESIDENTS_FEATURES:
            for c in pf:
                if hasattr(c, '__iter__'):
                    for feature in c:
                        all_features[feature[0]] = feature[1]

        for feature in self.presidents_features:
            result.append(all_features[feature])
        return result

class KidsProposal(PopularProposal):
    gathering = models.ForeignKey(KidsGathering,
                                  related_name='proposals',
                                  null=True)

    card_template = "votita/card.html"

    class Meta:
        verbose_name = _(u'Medida')
        verbose_name_plural = _(u"Medidas")

    def get_absolute_url(self):
        return reverse('votita:proposal_detail', kwargs={'slug': self.slug})

    @property
    def is_kids(self):
        return True
