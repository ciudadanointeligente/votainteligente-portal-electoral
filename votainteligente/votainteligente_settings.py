# coding=utf-8
DEFAULT_CANDIDATE_EXTRA_INFO = {
    "portrait_photo": "/static/img/candidate-default.jpg",
    'custom_ribbon': 'ribbon text'
}
DEFAULT_ELECTION_EXTRA_INFO = {
    "extra": "Extra extra extra"
}
NAV_BAR = ('profiles', 'questionary', 'soulmate', 'facetoface', 'ask', 'ranking')
THEME = None
NOTIFY_CANDIDATES_WHEN_MANY_PROPOSALS_REACH_A_NUMBER = True
WHEN_TO_NOTIFY = [25, 50, 100, 150, 200]
NOTIFY_CANDIDATES = True
NOTIFY_CANDIDATES_OF_NEW_PROPOSAL = True
MAX_AMOUNT_OF_MAILS_TO_CANDIDATE = 3
RECOMMENDED_ORGS_FROM_CACHE = True
# El tipo de area territorial que sirve para listar propuestas en /propuestas 
FILTERABLE_AREAS_TYPE = ['Comuna']
## No muestres las areas en el wizard de creación de propuestas
DONT_SHOW_AREAS_IN_PROPOSAL_WIZARD = True
DEFAULT_EXTRAPAGES_FOR_ORGANIZATIONS=[{'title':u'Agenda', 'content':'''* **19 DE NOVIEMBRE**\r\nPrimera vuelta de Elecciones Presidenciales y Parlamentarias
* **17 DE DICIEMBRE**   *Segunda vuelta de Elecciones Presidenciales'''},
                                                           {'title':u'Documentos', 'content':''}]
#Este es el candidato que aparece enel landing
IMPORTANT_CANDIDATE_IN_LANDING = None
MODERATION_ENABLED = False
MARKED_AREAS = []
POSSIBLE_GENERATING_AREAS_FILTER = []
EXCLUDED_PROPOSALS_APPS = []
AREAS_THAT_SHOULD_BE_REDIRECTING_TO_THEIR_PARENTS = ['comuna']
SECOND_ROUND_ELECTION = None
PRIORITY_CANDIDATES = []
# Candidatos en la parte de /candidaturas aparecen
LIST_ONLY_COMMITED_CANDIDATES = False
# Colores para compartir imagen de una propuesta
SHARED_PROPOSAL_IMAGE_ID_COLOR = (122,183,255,255)
EAGER_USER_IMAGE = True
MEDIA_NARANJA_QUESTIONS_ENABLED=True
# Esto sólo funciona para Brasil y para cargar los datos
#Desde El TSE
TSE_IMPORTER_CONF = None
ORGANIZATIONS_IN_12_RESULT = True
# TSE_DATE_FORMAT = "%Y/%m/%d"
