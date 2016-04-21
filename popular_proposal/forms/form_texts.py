# coding=utf-8

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

TEXTS = {
    'problem': {'label': u'Según la óptica de tu organización, describe un problema de la comuna que quieran solucionar. (2 líneas)',
                'help_text': u'Ej: Poca participación en el Plan Regulador, Falta de transparencia en el trabajo de la municipalidad, Pocos puntos de reciclaje, etc.',
                'placeholder': u'Tu problema'},
    'solution': {'label': u'¿Qué debería hacer la municipalidad para solucionar el problema? (3 líneas)',
                 'help_text': u'Ejemplo: "Crear una ciclovia que circunvale Valdivia", "Que se publiquen todos los concejos municipales en el sitio web del municipio".',
                 'placeholder': u'Tu solución'},
    'solution_at_the_end': {'label': u'Describe la medida específica que quieren solicitar a los candidatos. ¿Qué avance concreto esperan que se logre durante el periodo del alcalde (4 años)?',
                            'help_text': u'Ejemplo: "Aumentar en un 20% la cantidad de ciclovías en la ciudad"',
                            'placeholder': u'1) Aumentar en un 20% la cantidad de ciclovías\n\r 2) Tener un estacionamiento de bicicletas en la calle Arturo Prat'},
    'when': {'label': u'¿En qué plazo debería estar implementada esta solución?',
                'help_text': u'',
                'placeholder': u''},
    'title': {'label': u'Resumen',
              'help_text': u'Escribe un título que nos permita describir tu propuesta ciudadana. Ej: 50% más de ciclovías para la comuna',
              'placeholder': u''},
    'classification': {'label': u'¿En qué área clasificarías tu propuesta?',
                       'help_text': u'',
                       'placeholder': u''},
    'allies': {'label': u'¿Quiénes son tus posibles aliados?',
               'help_text': u'',
               'placeholder': u''},
    'organization': {'label': u'¿Estás haciendo esta propuesta a nombre de una organización? Escribe su nombre acá:',
                     'help_text': u'',
                     'placeholder': u''},
}
