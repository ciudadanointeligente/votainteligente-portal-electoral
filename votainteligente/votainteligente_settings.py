# coding=utf-8
import sys
import os
from django.conf import settings

DEFAULT_CANDIDATE_EXTRA_INFO = {
    "portrait_photo": "/static/img/candidate-default.jpg",
    'custom_ribbon': 'ribbon text'
}
DEFAULT_ELECTION_EXTRA_INFO = {
    "extra": "Extra extra extra"
}

SOCIAL_AUTH_FACEBOOK_KEY = ''
SOCIAL_AUTH_FACEBOOK_SECRET = ''
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    'fields': 'id,name,email',
}
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = ''
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = ''
LOGIN_ERROR_URL = '/'
SOCIAL_AUTH_LOGIN_ERROR_URL = '/'

# navigation bar
NAV_BAR = ('profiles', 'questionary', 'soulmate', 'facetoface', 'ask', 'ranking')
THEME = None
WHEN_TO_NOTIFY = [25, 50, 100, 150, 200]
NOTIFY_CANDIDATES = True
NOTIFY_CANDIDATES_OF_NEW_PROPOSAL = True
NO_REPLY_MAIL = "no-reply@localhost"
EMAIL_LOCALPART = 'municipales2016'
EMAIL_DOMAIN = 'votainteligente.cl'
MAX_AMOUNT_OF_MAILS_TO_CANDIDATE = 3
FILTERABLE_AREAS_TYPE = ['Comuna']

DEFAULT_EXTRAPAGES_FOR_ORGANIZATIONS=[{'title':u'Agenda', 'content':'''* **19 DE NOVIEMBRE**\r\nPrimera vuelta de Elecciones Presidenciales y Parlamentarias
* **17 DE DICIEMBRE**   *Segunda vuelta de Elecciones Presidenciales'''},
                                                           {'title':u'Documentos', 'content':''}]

FACEBOOK_ACCESS_TOKEN = 'FieraEsLaMejorAmigaDeTodos'
MODERATION_ENABLED = False
POSSIBLE_GENERATING_AREAS_FILTER = []
EXCLUDED_PROPOSALS_APPS = ['votita', ]
AREAS_THAT_SHOULD_BE_REDIRECTING_TO_THEIR_PARENTS = ['comuna']
SECOND_ROUND_ELECTION = None
PRIORITY_CANDIDATES = []

TESTING = 'test' in sys.argv
if TESTING:
    from testing_settings import *
else:
    try:
        from local_settings import *
    except ImportError, e:
        pass