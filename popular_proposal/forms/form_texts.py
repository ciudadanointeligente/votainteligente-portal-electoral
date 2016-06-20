# coding=utf-8

WHEN_CHOICES = [
    ('', '----'),
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
    'problem': {'label': u'',
                'help_text': u'',
                'placeholder': u'¿Cuál es el problema que afecta a la comuna (o barrio) de la que el alcalde debe hacerse cargo?',
                'long_text': "paso1.html"},
    'causes': {'label': u'',
               'help_text': u'',
               'placeholder': u'Utilizen el ejercicio de los "por qués"',
               'long_text': "paso2.html"},
    'solution': {'label': u'',
                 'help_text': u'',
                 'placeholder': u'Tu solución',
                 'long_text': "paso3.html"},
    'solution_at_the_end': {'label': u'',
                            'help_text': u'',
                            'placeholder': u'Que la Municipalidad de Pelarco destine un 20% más de recursos al año para colegios o liceos.\n\rQue la Municipalidad de Pelarco elabore e implemente un plan junto a los profesores de Educación Media para optimizar los recursos en educación.',
                            'long_text': "paso4a.html"},
    'when': {'label': u'',
             'help_text': u'6_months',
             'placeholder': u'',
             'long_text': "paso4b.html"},
    'title': {'label': u'',
              'help_text': u'',
              'placeholder': u'Mejoremos la educación en la comuna',
              'long_text': "paso5a.html"},
    'clasification': {'label': u'',
                      'help_text': u'transparencia',
                      'placeholder': u'',
                      'long_text': "paso5b.html"},
    'organization': {'label': u'',
                     'help_text': u'',
                     'placeholder': u'',
                     'long_text': "organization.html"},
}
