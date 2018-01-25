# coding=utf-8
import sys
import os
from django.conf import settings
from datetime import timedelta
from django.conf import settings


DEFAULT_CANDIDATE_EXTRA_INFO = {
    "portrait_photo": "/static/img/candidate-default.jpg",
    'custom_ribbon': 'ribbon text'
}
DEFAULT_ELECTION_EXTRA_INFO = {
    "extra": "Extra extra extra"
}

TESTING = 'test' in sys.argv





CELERYBEAT_SCHEDULE = {'sending-new-proposals-once-a-day': {'task': 'proposal_subscriptions.tasks.send_new_proposals_to_subscribers',
                                                         'schedule': timedelta(days=1),
                                                         },
                       'new-commitments-notifications': {'task': 'proposal_subscriptions.tasks.send_commitment_notifications',
                                                                                'schedule': timedelta(days=7),
                                                                                },
                       # 'letting-candidates-know-about-us-every-two-days':
                       # {'task': 'backend_candidate.tasks.send_candidates_their_username_and_password',
                       #                                                     'schedule': timedelta(days=2),
                       #                                                     },
                       }

if TESTING:

    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'haystack.backends.elasticsearch2_backend.Elasticsearch2SearchEngine',
            'URL': 'http://127.0.0.1:9200/',
            'INDEX_NAME': 'votainteligente_test',
        },
    }
else:
    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'haystack.backends.elasticsearch2_backend.Elasticsearch2SearchEngine',
            'URL': 'http://127.0.0.1:9200/',
            'INDEX_NAME': 'votainteligente',
        },
    }
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'
# SOUTH_TESTS_MIGRATE = False
EXTRA_APPS = ()

# navigation bar
# NAV_BAR = ('profiles','questionary','soulmate','facetoface','ask','ranking')
NAV_BAR = ('profiles', 'questionary', 'soulmate', 'facetoface', 'ask', 'ranking')
WEBSITE_METADATA = {
    'author': u'Name of the author',
    'description': u'A description for the site',
    'keywords': u'some,tags,separated,by,comma'
}
# for Facebook OGP http://ogp.me/
WEBSITE_OGP = {
    'title': u'VotaInteligente',
    'type': 'website',
    'url': 'http://www.mi-domain.org/',
    'image': 'img/votai-196.png',
    'fb:app_id': 'APPID'
}
# disqus setting dev
WEBSITE_DISQUS = {
    'enabled': True,
    'shortname': 'shortname_disqus',
    'dev_mode': 0
}
# google analytics
WEBSITE_GA = {
    'code': 'UA-XXXXX-X',
    'name': 'ga_name',
    'gsite-verification': 'BCyMskdezWX8ObDCMsm_1zIQAayxYzEGbLve8MJmxHk'
}
# imgur
WEBSITE_IMGUR = {
    #  example client_id, only works with 50 pic a day
    'client_id': 'eb18642b5b220484864483b8e21386c3',
}
# settings for global site
WEBSITE_GENERAL_SETTINGS = {
    'home_title': 'Lorem ipsum dolor sit amet, consectetur adipisicing elit.'
}
# twitter sepparated by comma, eg: votainteligente,votainformado,othertag
# WEBSITE_TWITTER = {
#     'hashtags': 'votainteligente',
#     'text': 'Conoce a tus candidat@s y encuentra a tu Media Naranja Política en '
# }
CACHE_MINUTES = 0
HEAVY_PAGES_CACHE_MINUTES = 1


THEME = None


WHEN_TO_NOTIFY = [25, 50, 100, 150, 200]
NOTIFY_CANDIDATES = True
NOTIFY_CANDIDATES_OF_NEW_PROPOSAL = True
NO_REPLY_MAIL = "no-reply@localhost"
EMAIL_LOCALPART = 'municipales2016'
EMAIL_DOMAIN = 'votainteligente.cl'
MAX_AMOUNT_OF_MAILS_TO_CANDIDATE = 3
FILTERABLE_AREAS_TYPE = ['Comuna']

# HIDDEN_AREAS = ['fundacion-ciudadano-inteligente', ]
DEFAULT_EXTRAPAGES_FOR_ORGANIZATIONS=[{'title':u'Agenda', 'content':'''* **19 DE NOVIEMBRE**\r\nPrimera vuelta de Elecciones Presidenciales y Parlamentarias
* **17 DE DICIEMBRE**	*Segunda vuelta de Elecciones Presidenciales'''},
                                                           {'title':u'Documentos', 'content':''}]


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
FACEBOOK_ACCESS_TOKEN = 'FieraEsLaMejorAmigaDeTodos'

# TWITTER_TOKEN = 'TWITTER_TOKEN'
# TWITTER_TOKEN_KEY = 'TWITTER_TOKEN_KEY'
# TWITTER_CON_KEY = 'TWITTER_CON_KEY'
# TWITTER_CON_SECRET_KEY = 'TWITTER_CON_SECRET_KEY'

MODERATION_ENABLED = False
MARKED_AREAS = ['teodoro-schmidt-9117','cunco-9103','lumaco-9207','melipeuco-9110','gorbea-9107','arica-15101','copiapo-3101','freirina-3303','caldera-3102','tortel-11303','guaitecas-11203','cisnes-11202','rio-ibanez-11402','santa-barbara-8311','contulmo-8204','alto-biobio-8314','treguaco-8420','los-alamos-8206','hualpen-8112','lota-8106','monte-patria-4303','los-vilos-4203','rio-hurtado-4305','la-higuera-4104','frutillar-10105','maullin-10108','castro-10201','puqueldon-10206','puyehue-10304','san-juan-de-la-costa-10306','puerto-montt-10101','corral-14102','futrono-14202','paillaco-14107','lago-ranco-14203','valdivia-14101','rauco-7305','rio-claro-7108','hualane-7302','san-clemente-7109','longavi-7403','talca-7101','constitucion-7102','coltauco-6104','machali-6108','paredones-6206','peralillo-6307','rengo-6115','quilicura-13125','curacavi-13503','independencia-13108','san-bernardo-13401','puente-alto-13201','penaflor-13605','pedro-aguirre-cerda-13121','huechuraba-13107','alto-hospicio-1107','san-antonio-5601','santa-maria-5706','llaillay-5703']

POSSIBLE_GENERATING_AREAS_FILTER = []
AREAS_THAT_SHOULD_BE_REDIRECTING_TO_THEIR_PARENTS = ['comuna']
SECOND_ROUND_ELECTION = None
PRIORITY_CANDIDATES = []
CONSTANCE_ADDITIONAL_FIELDS = {
    'proposals_getter_for_12_n': ['django.forms.fields.ChoiceField', {
        'widget': 'django.forms.Select',
        'choices': (("getter", "por corazones"), ("reading_group", "grupos de lectura"))
    }],
}
CONSTANCE_CONFIG = {
    'SOUL_MATE_INFO_ABOUT_CANDIDATES_MINUTES':(0,'Duracion cache media naranja'),
    'INFINITE_CACHE':(1440,'Tiempo Cache'),
    'DEFAULT_AREA': ('chile-pais', u'El territorio que mostramos por defecto'),
    'AREAS_ARE_FORCED_IN_PROPOSALS' : (False, u'No te preguntamos por el territorio de la propuesta y asumimos que es el que viene por defecto'),
    'PROPOSALS_ENABLED' : (True, 'Habilitar propuestas'),
    'WHEN_TO_NOTIFY': ('25, 50, 100, 150, 200', 'Cuando notificar'),
    'NOTIFY_CANDIDATES': (True, 'Notificar a los candidatos'),
    'NOTIFY_STAFF_OF_NEW_COMMITMENT': (True, 'Notificar al staff si es que hay un nuevo compromiso'),
    'NOTIFY_CANDIDATES_OF_NEW_PROPOSAL': (True, 'Notificar a los candidatos por una nueva propuesta'),
    'CAN_CANDIDATES_NOT_COMMIT': (False, 'Pueden los candidatos NO comprometerse?'),
    'NO_REPLY_MAIL': ("no-reply@localhost", 'Cuenta email de envio de correos'),
    'EMAIL_LOCALPART': ("municipales2016", 'Cuenta email localhost'),
    'EMAIL_DOMAIN': ("votainteligente.cl", 'Nombre dominio'),
    'MAX_AMOUNT_OF_MAILS_TO_CANDIDATE': (3, 'Numero maximo de envios de emails a candidatos'),
    'TWITTER_TOKEN': ('', 'Twitter token'),
    'MARKED_AREAS': (", ".join(MARKED_AREAS), u'Areas que tienen alguna marca'),
    'CANDIDATE_ABSOLUTE_URL_USING_AREA': (True, u'para ver el perfil de los candidatos utilziamos el territorio o utilizamos la elección a la que pertenece?'),
    'TWITTER_TOKEN_KEY': ('', 'Twitter token key'),
    'TWITTER_CON_KEY': ('', 'Twitter connection key'),
    'TWITTER_CON_SECRET_KEY': ('', 'Twitter connection secret key'),
    'HIDDEN_AREAS': ('', 'Seccion oculta'),
    'NAV_BAR': ('profiles, questionary, soulmate, facetoface, ask, ranking', 'Menu de navegacion'),
    'NAV_BAR_VOTITA_DISPLAYED': (False, 'Desplegamos el navbar del votita??????'),
    'SHOW_RIBBON_IN_CANDIDATE': (False, u"Debería aparecerles la franja roja que dice 'No se ha compormetido?'"),
    'CAN_CREATE_TEST_PROPOSAL': (False, u'Se pueden crear propuestas de prueba?'),
    'CANDIDATES_ARE_DISPLAYED': (False, u'Se muestra el menú "Conoce tus candidatos"?(recuerda que si eres staff lo verás igual no más sin importar esta wea)'),
    'SEARCH_SUBSCRIPTION_ENABLED': (True, u'Suscribirse a una búsqueda está habilitado? esto sólo esconde los links.'),
    'WEBSITE_METADATA_AUTHOR': ('', 'Nombre del autor'),
    'WEBSITE_METADATA_DESCRIPTION': ('', 'Descripcion del sitio'),
    'WEBSITE_METADATA_KEYWORD': ('', 'Palabras claves del sitio'),
    'WEBSITE_OGP_TITLE': ('VotaInteligente', 'Titulo OpenGraph Protocol'),
    'WEBSITE_OGP_TYPE': ('website', 'Tipo OpenGraph Protocol'),
    'WEBSITE_OGP_URL': ('https://www.mi-domain.org/', 'URL base OpenGraph Protocol'),
    'WEBSITE_OGP_DESCRIPTION': ('', 'Descripción del sitio para OpenGraph Protocol'),
    'WEBSITE_OGP_APP_ID': ('APPID', 'Facebokk App ID'),
    'WEBSITE_DISQUS_ENABLED': (True, 'Activar Disqus'),
    'WEBSITE_DISQUS_SHORTNAME': (True, 'Disqus shortname'),
    'WEBSITE_DISQUS_DEV_MODE': (False, 'Modo desarrollo'),
    'WEBSITE_GA_CODE': ('UA-XXXXX-X', 'Codigo Google Analytics'),
    'WEBSITE_GA_NAME': ('votainteligente.cl', 'Nombre Google Analytics'),
    'WEBSITE_GA_GSITE_VERIFICATION': ('BCyMskdezWX8ObDCMsm_1zIQAayxYzEGbLve8MJmxHk', 'Verificacion Google Site'),
    'WEBSITE_IMGUR_CLIENT_ID': ('eb18642b5b220484864483b8e21386c3', 'Imgur'),
    'WEBSITE_GENERAL_SETTINGS_HOME_TITLE': ('Lorem ipsum dolor sit amet, consectetur adipisicing elit.', 'Titulo Home'),
    'WEBSITE_TWITTER_HASHTAG': ('votainteligente', 'Twitter Hashtags'),
    'WEBSITE_TWITTER_TEXT': ('Conoce a tus candidat@s y encuentra a tu Media Naranja Política en', 'Texto twitts'),
    'AYUDANOS_TEXTO1' : (u'Tenemos poca info de candidatos. Ayuda a candidatos y electores haciendo que respondan la ½ naranja', 'texto 1 del ayudanos'),
    'AYUDANOS_TEXTO2' : (u'Si no conoces a tus candidatos y no sabes ', 'texto 2 del ayudanos'),
    'AYUDANOS_TEXTO3' : (u'Invita a tus candidatos a dejar su información en VotaInteligente.cl para saber qué piensan y ', 'texto 3 del ayudanos'),
    'AYUDANOS_TEXTO4' : (u'Necesitamos que los candidatos compartan su infromación con los vecinos, para conocerlos y saber ', 'texto 4 del ayudanos'),
    'AYUDANOS_ORGANIZACIONES' : (u'Ya puedes comprometerte con nuestras propuestas ', 'texto ayudanos en las organizaciones'),
    "CANDIDATE_SEARCH_ENABLED": (True, 'La busqueda de candidatos está habilitada???'),
    'AYUDANOS_TEXTO_CANDIDATOS' : (u'Ya puedes comprometerte con nuestras propuestas ', 'texto a los candidatos del ayudanos'),
    'AYUDANOS_PROPUESTA': (u'Ya puedes comprometerte en votainteligente.cl', 'texto a los candidatos del ayudanos específico de cada propuesta'),
    'MOSTRAR_AYUDANOS_PROPUESTA': (False, 'texto a los candidatos del ayudanos específico de cada propuesta'),
    'DEFAULT_12_N_QUESTIONS_IMPORTANCE': (0.5, "Importancia de las preguntas en la media naranja"),
    'DEFAULT_12_N_PROPOSALS_IMPORTANCE': (0.5, "Importancia de las propuestas en la media naranja"),
    'SHOW_MAIL_NOT_TEMPLATE': (True, 'mostrar el mail que se envía en lugar de un html'),
    'N_CANDIDATOS_RESULTADO_12_N': (3, u'Máximo número de candidatos en el resultado de la 1/2 Naranja'),
    'MEDIA_NARANJA_MAX_NUM_PR': (20, u'Máximo número de propuestas listadas en la 1/2 Naranja'),
    'MEDIA_NARANJA_MAX_SELECT_PROPOSALS': (5, u'Máximo número de propuestas seleccionables en la 1/2 Naranja'),
    'PRUEBAS_DE_CARGA_MEDIA_NARANJA': (False, u'Esto baja el csrf para las pruebas de la medianaranja2'),
    'ESTRATEGIA_SELECCION_PROPUESTAS': ("getter", u'Qué estrategia usamos para mostrar propuestas en la 1/2 naranja', 'proposals_getter_for_12_n'),
}

try:
    from local_settings import *
except ImportError, e:
    pass

if TESTING:
    from testing_settings import *
