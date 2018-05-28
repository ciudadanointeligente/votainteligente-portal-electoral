# coding=utf-8
from collections import OrderedDict
from django.utils.translation import ugettext as _
from django.conf import settings
import importlib

WHEN_CHOICES = [
    ('', _(u'Selecciona cuándo')),
    ('1_year', _(u'1 año')),
    ('2_year', _(u'2 años')),
    ('3_year', _(u'3 años')),
    ('4_year', _(u'4 años')),
]

_TOPIC_CHOICES = (('', _(u'Selecciona una categoría')),
                 ('asistencia', _(u'Asistencia y protección social')),
                 ('ciencias', _(u'Ciencias')),
                 ('cultura', _(u'Cultura')),
                 ('democracia', _(u'Democracia')),
                 ('deporte', _(u'Deporte')),
                 ('derechoshumanos', _(u'Derechos Humanos')),
                 ('derechos', _(u'Derechos Sociales')),
                 ('descentralizacion', _(u'Descentralización')),
                 ('emergencia', _(u'Desastres Naturales')),
                 ('economia', _(u'Economía')),
                 ('educacion', _(u'Educación')),
                 ('empleo', _(u'Empleo')),
                 ('emprendimiento', _(u'Emprendimiento')),
                 ('energia', _(u'Energía')),
                 ('genero', _(u'Equidad y género')),
                 ('diversidad', _(u'Inclusión')),
                 ('institucionespublicas', _(u'Instituciones Públicas')),
                 ('infancia', _(u'Infancia y juventud')),
                 ('justicia', _(u'Justicia')),
                 ('medioambiente', _(u'Medio ambiente')),
                 ('medios', _(u'Medios de comunicación')),
                 ('migracion', _(u'Migración')),
                 ('mineria', _(u'Minería')),
                 ('ocio', _(u'Ocio')),
                 ('pensiones', _(u'Pensiones')),
                 ('participacion', _(u'Participación')),
                 ('prevision', _(u'Previsión')),
                 ('probidad', _(u'Probidad')),
                 ('proteccionsocial', _(u'Protección social')),
                 ('pueblosoriginarios', _(u'Pueblos originarios')),
                 ('recursosnaturales', _(u'Recursos naturales')),
                 ('salud', _(u'Salud')),
                 ('seguridad', _(u'Seguridad')),
                 ('sustentabilida', _(u'Sustentabilidad')),
                 ('terceraedad', _(u'Adulto mayor')),
                 ('proteccionanimal', _(u'Protección animal')),
                 ('trabajo', _(u'Trabajo')),
                 ('transparencia', _(u'Transparencia')),
                 ('transporte', _(u'Transporte')),
                 ('espaciospublicos', _(u'Urbanismo y Espacios públicos')),
                 )
def get_topic_choices():
    if settings.THEME:
        proposals_mod = '%s.proposals_categories' % settings.THEME
        try:
            m = importlib.import_module(proposals_mod)
            topics_from_theme = getattr(m, '_TOPIC_CHOICES')
            return topics_from_theme
        except Exception as e:
            pass

    return _TOPIC_CHOICES

TOPIC_CHOICES = get_topic_choices()

TOPIC_CHOICES_DICT = dict(TOPIC_CHOICES)
TEXTS = OrderedDict({
    'problem': {'label': _(u'El problema que se quiere solucionar es'),
                'preview_question': _(u'¿Cuál es el problema que quieres solucionar?'),
                'help_text': _(u'Contaminación en la ciudad'),
                'placeholder': _(u'Escribe el problema que quieres solucionar con tu propuesta.'),
                },
    'causes': {'label': _(u'La causa de este problema es'),
               'preview_question': _(u'Cuáles son las causas de este problema?'),
               'placeholder': _(u'Escribe aquí la causa de tu problema que quieres abordar. Recuerda solo escribir una.'),
               'long_text': "causes_help.html"},
    'one_liner': {'label': _(u'Si yo fuera un candidato electo, mi primera medida sería...'),
               'preview_question': _(u'Cuáles son las causas de este problema?'),
               'help_text': _(u"Crear una ley para regular el uso de bolsas plásticas"),
               'placeholder': _(u'Escribe la propuesta como si fuera tu primera medida como presidenta o presidente. '),
               },
    'solution': {'label': _(u'¿Cuáles posibles soluciones creemos que existen para pasar del problema a la situación ideal?'),
                 'preview_question': _(u'¿Cual sería la situación ideal?'),
                 'help_text': u"",
                 'placeholder': _(u'Escribe aquí la situación ideal a la que quieres llegar.'),
                 'long_text': "paso3.html"},
    'solution_at_the_end': {'label': _(u'La propuesta para solucionar este problema es'),
                            'preview_question': _(u'¿Cuál sería la solución?'),
                            'help_text': _(u'Se puede regular el uso de bolsas plásticas en los supermercados a solo tres por persona, las otras bolsas que se usen deben ser reutilizables.'),
                            'placeholder': _(u'Escribe aquí la solucion para el problema que definiste.')},
    'when': {'label': _(u'Tiempo en el cual se puede llevar a cabo la propuesta'),
             'preview_question': _(u'¿Cuándo debería estar esto listo?'),
             'help_text': _(u'1 año'),
             'placeholder': u"",},
    'title': {'label': _(u'Colócale título'),
              'preview_question': _(u'Título'),
              'help_text': u"",
              'placeholder': _(u'Título de la propuesta'),
              'long_text': ""},
    'clasification': {'label': _(u'Selecciona una categoría'),
                      'preview_question': _(u'Clasificación'),
                      'help_text': _(u'Medio ambiente'),
                      'placeholder': u"",
                      'long_text': ""},
    'is_local_meeting': {'label': _(u'¿Esta propuesta es producto de un encuentro local?'),
                      'preview_question': _(u'¿Es un encuentro local?'),
                      'help_text': u"",
                      'placeholder': u"",
                      'long_text': "is_local_meeting.html"},
    'generated_at': {'label': _(u'¿En qué comuna se generó esta propuesta?'),
                      'preview_question': _(u'¿Es un encuentro local?'),
                      'help_text': _(u'Si eres una ONG de vocación nacional, esta opción no aplica'),
                      'placeholder': u"",
                      'long_text': "generated_at.html"},
    'terms_and_conditions': {'label': _(u'Términos y condiciones'),
                             'preview_question': u"",
                             'help_text': u"",
                             'placeholder': u"",
                             'long_text': "terms_and_conditions.html"},
    'is_testing': {'label': _(u'Esta propuesta es de prueba'),
                             'preview_question': u"",
                             'help_text': _(u'Sólo la podrás ver tu y nosotros podremos borrarlas periodicamente.'),
                             'placeholder': u"",
                             'long_text': ""},
})

SEARCH_ELEMENTS_FROM_DATA = [
  'problem','solution','causes', 'solution_at_the_end', 'when'
]
