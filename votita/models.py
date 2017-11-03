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
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import textwrap

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
    comments = models.TextField(verbose_name=u"¿Cómo podemos empoderar mejor a nuestros niños?",
                                blank=True,
                                default=u"")
    school = models.CharField(max_length=512,
                            verbose_name="Establecimiento u organización",
                            blank=True)

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

COLORS = {"diversidad":  "#CB78D3",
          "salud":  "#7AB7FF",
          "medio_ambiente":  "#49B172",
          "politica":  "#FEC70D",
          "educacion_y_trabajo":  "#FA589A",
          "cultura":  "#FF645B",
          "tecnologia": "#7AB7FF",
          "proteccion_y_familia": "#FEC70D",
          }

class KidsProposal(PopularProposal):
    gathering = models.ForeignKey(KidsGathering,
                                  related_name='proposals',
                                  null=True)

    card_template = "votita/card.html"
    detail_template_html = "votita/plantillas/detalle_propuesta.html"

    def generate_og_image(self):
        plantilla = Image.open('votai_general_theme/static/img/plantilla_llm.png')

        font_n_propuesta = ImageFont.truetype("votai_general_theme/static/fonts/Nunito-Black.ttf", 24)
        font_titulo = ImageFont.truetype("votai_general_theme/static/fonts/Nunito-Black.ttf", 76)
        font_autor = ImageFont.truetype("votai_general_theme/static/fonts/WorkSans-Bold.ttf", 21)
        bg_color = COLORS[self.clasification]
        output = BytesIO()
        output.seek(0)
        h = bg_color.lstrip('#')
        rgb_color = tuple(int(h[i:i+2], 16) for i in (0, 2 ,4))
        rgb_color = rgb_color
        base = Image.new('RGBA',(1200,630),rgb_color)
        txt = Image.new('RGBA', base.size, (122,183,255,0))
        d = ImageDraw.Draw(txt)
        n_propuesta = u"Propuesta N º"+ unicode(self.id)
        n_propuesta = n_propuesta.upper()
        d.multiline_text((106,73), n_propuesta, font=font_n_propuesta, fill=(0,0,0))

        lines = textwrap.wrap(self.title, width=30)
        max_lines = 3
        if len(lines) > max_lines:
            last_line = lines[max_lines - 1] + u'...'
            lines = lines[0:max_lines]
            lines[max_lines - 1] = last_line

        title = '\n'.join(lines)

        fg_color = (255, 255, 255)
        d.multiline_text((106,129), title, font=font_titulo, fill=fg_color)
        
        proposer_name = self.gathering.name
        propuesta_de = proposer_name
        d.multiline_text((106,448), propuesta_de, font=font_autor, fill=(0,0,0))


        base = Image.alpha_composite(base, txt)
        base.paste(plantilla, (0,0), plantilla)
        return base

    @classmethod
    def get_topic_choices_dict(cls):
        from votita.forms.forms import TOPIC_CHOICES_DICT
        return TOPIC_CHOICES_DICT

    @property
    def ribbon_text(self):
        return u"Propuesta generada por niñas, niños y adolescentes"

    class Meta:
        verbose_name = _(u'Medida')
        verbose_name_plural = _(u"Medidas")

    def get_absolute_url(self):
        return reverse('votita:proposal_detail', kwargs={'slug': self.slug})

    @property
    def is_kids(self):
        return True
