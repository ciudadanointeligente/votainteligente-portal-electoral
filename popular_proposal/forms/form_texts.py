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
    'problem': {'label': u'¿Cuál es el problema que afecta a la comuna (o barrio) de la que el alcalde debe hacerse cargo?',
                'help_text': u'Los alumnos de los liceos municipales de la comuna de Pelarco obtuvieron en su mayoría bajo 500 puntos en la PSU del proceso de admisión 2016.',
                'placeholder': u'Tu problema',
                'long_text':"problem.html",
                'step': u'Paso 1'},
    'ideal_situation': {'label': u'Describan el objetivo que quieren alcanzar con la solución que van a proponer:',
               'help_text': u'Ejemplo: El año 2020, el 50% de los alumnos de los liceos municipales de la comuna de Pelarco obtendrán más de 500 puntos en la PSU.',
               'placeholder': u'',
               'long_text':"ideal_situation.html",
               'step': u'Paso 1'},
    'causes': {'label': u'¿Por qué existe el problema? Identifiquen de dónde proviene el problema.',
               'help_text': u'',
               'placeholder': u'Utiliza la técnica de los 3 por qués',
               'long_text':"causes.html",
               'step': u'Paso 1'},
    'solution': {'label': u'¿Cómo se puede lograr la situación ideal? Propongan la(s) medida(s) que el alcalde debe tomar para solucionar la causa del problema y poder alcanzar la situación ideal.',
                 'help_text': u'Ej: Que la Municipalidad de Pelarco otorgue más recursos para educación.',
                 'placeholder': u'Tu solución',
                 'long_text':"solution.html",
                 'step': u'Paso 1'},
    'solution_at_the_end': {'label': u'¿Qué acción dará por cumplida la tarea del alcalde? Definan detalladamente qué debe hacer el alcalde/municipalidad como solución al problema:',
                            'help_text': u'Ejemplos:\n\rQue la Municipalidad de Pelarco destine un 20% más de recursos al año para colegios o liceos.\n\rQue la Municipalidad de Pelarco elabore e implemente un plan junto a los profesores de Educación Media para optimizar los recursos en educación.',
                            'placeholder': u'Que la Municipalidad de Pelarco destine un 20% más de recursos al año para colegios o liceos.\n\rQue la Municipalidad de Pelarco elabore e implemente un plan junto a los profesores de Educación Media para optimizar los recursos en educación.',
                            'long_text':"solution_at_the_end.html",
                            'step': u'Paso 1'},
    'when': {'label': u'¿En qué plazo debe quedar lista la acción que proponen? Escriban de nuevo la solución que proponen, agregando el tiempo en que el alcalde debe dejarla lista:',
                'help_text': u'Ejemplos: Que la Municipalidad de Pelarco destine un 20% más de recursos al año para colegios o liceos a partir del segundo año del alcalde.Que para el año 2018 la Municipalidad de Pelarco elabore e implemente un plan junto a los profesores de Educación Media para optimizar los recursos en educación. ',
                'placeholder': u'',
                'long_text':"when.html",
                'step': u'Paso 1'},
    'title': {'label': u'Pónganle un título a modo de resumen para su propuesta y después escojan dentro de las opciones en qué tema se clasificaría.',
              'help_text': u'Ejemplo: Más recursos para educación en Pelarco, Tema: Educación',
              'placeholder': u'',
              'long_text':"title.html",
              'step': u'Paso 1'},
    'clasification': {'label': u'Clasificación',
                       'help_text': u'Educación',
                       'placeholder': u'',
                       'long_text':"clasification.html",
                       'step': u'Paso 1'},
    'organization': {'label': u'¿Estás haciendo esta propuesta a nombre de una organización? Selecciona:',
                     'help_text': u'',
                     'placeholder': u'',
                     'long_text':"organization.html",
                     'step': u'Paso 1'},
}
