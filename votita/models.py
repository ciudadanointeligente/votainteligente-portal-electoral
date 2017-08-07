# coding=utf-8
from __future__ import unicode_literals
from django.db import models
from django.template.loader import get_template
from picklefield.fields import PickledObjectField
from popular_proposal.models import PopularProposal
from multiselectfield import MultiSelectField


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
    name = models.CharField(max_length=512,
                            verbose_name="Nombre del encuentro")
    stats_data = PickledObjectField()
    presidents_features = MultiSelectField(choices=PRESIDENTS_FEATURES,
                                           null=True,
                                           max_choices=10,
                                           max_length=512,
                                           verbose_name="Características de un buen presidente")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='votita/images/',
                              max_length=512,
                              null=True,
                              blank=True,
                              verbose_name="Foto del encuentro")


class KidsProposal(PopularProposal):
    gathering = models.ForeignKey(KidsGathering,
                                  related_name='proposals',
                                  null=True)
    @property
    def is_kids(self):
        return True

    @property
    def card(self):
        return get_template("votita/card.html").render({
            'proposal': self
        })
