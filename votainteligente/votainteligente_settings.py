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
WHEN_TO_NOTIFY = [25, 50, 100, 150, 200]
NOTIFY_CANDIDATES = True
NOTIFY_CANDIDATES_OF_NEW_PROPOSAL = True
MAX_AMOUNT_OF_MAILS_TO_CANDIDATE = 3
FILTERABLE_AREAS_TYPE = ['Comuna']
DEFAULT_EXTRAPAGES_FOR_ORGANIZATIONS=[{'title':u'Agenda', 'content':'''* **19 DE NOVIEMBRE**\r\nPrimera vuelta de Elecciones Presidenciales y Parlamentarias
* **17 DE DICIEMBRE**   *Segunda vuelta de Elecciones Presidenciales'''},
                                                           {'title':u'Documentos', 'content':''}]

MODERATION_ENABLED = False
MARKED_AREAS = []
POSSIBLE_GENERATING_AREAS_FILTER = []
EXCLUDED_PROPOSALS_APPS = []
AREAS_THAT_SHOULD_BE_REDIRECTING_TO_THEIR_PARENTS = ['comuna']
SECOND_ROUND_ELECTION = None
PRIORITY_CANDIDATES = []