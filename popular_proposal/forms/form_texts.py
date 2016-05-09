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
    'problem': {'label': u'Describe el problema de la comuna que proponen solucionar. (Max. 2 líneas)',
                'help_text': u'Ej: “Poca participación en el Plan Regulador”, “No se fomenta el uso de bicicletas”, “Falta de transparencia en el trabajo de la municipalidad”, “Pocos puntos de reciclaje”.',
                'placeholder': u'Tu problema'},
    'solution': {'label': u'¿Qué debería hacer el alcalde para solucionar el problema? Describe la solución. (Max. 3 líneas)',
                 'help_text': u'Ejemplo: "Consultar a los vecinos antes de cambiar el Plan Regulador”, “Habilitar ciclovías en las avenidas principales de la comuna", "Que se publiquen todos los concejos municipales en el sitio web del municipio", “Aumentar los puntos de reciclaje”',
                 'placeholder': u'Tu solución'},
    'solution_at_the_end': {'label': u'Ponle una cifra a tu solución para medir al término del período si se hizo o no se hizo (cantidad de unidades, porcentajes, etc.).',
                            'help_text': u'Ejemplo: “Realizar una consulta ciudadana 6 meses antes de cambiar el Plan Regulador","Aumentar en un 20% la cantidad de ciclovías en la comuna", "Poner 5 puntos de reciclaje nuevos en la comuna”',
                            'placeholder': u'1) Aumentar en un 20% la cantidad de ciclovías\n\r2) Tener un estacionamiento de bicicletas en la plaza Arturo Prat'},
    'when': {'label': u'¿En qué plazo debería estar implementada esta solución?',
                'help_text': u'Ejemplo: “Durante los primeros 6 meses”, “Al cumplirse un año”',
                'placeholder': u''},
    'title': {'label': u'Resumen',
              'help_text': u'Escribe un título que nos permita describir tu propuesta ciudadana. Ej: 50% más de ciclovías para la comuna',
              'placeholder': u''},
    'classification': {'label': u'¿En qué área clasificarías tu propuesta?',
                       'help_text': u'',
                       'placeholder': u''},
    'allies': {'label': u'¿Quiénes pueden ayudar a difundir esta propuesta?',
               'help_text': u'',
               'placeholder': u''},
    'organization': {'label': u'¿Estás haciendo esta propuesta a nombre de una organización? Selecciona:',
                     'help_text': u'',
                     'placeholder': u''},
}
