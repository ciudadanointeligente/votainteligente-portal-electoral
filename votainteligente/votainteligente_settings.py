# coding=utf-8
import sys
import os
from django.conf import settings
from datetime import timedelta
from django.conf import settings
from django_nose import NoseTestSuiteRunner


DEBUG = True
DEFAULT_CANDIDATE_EXTRA_INFO = {
    "portrait_photo": "/static/img/candidate-default.jpg",
    'custom_ribbon': 'ribbon text'
}
DEFAULT_ELECTION_EXTRA_INFO = {
    "extra": "Extra extra extra"
}

TESTING = 'test' in sys.argv
INSTALLED_APPS = (
    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.flatpages',
    'django_nose',
    'django.contrib.sitemaps',
    'linaro_django_pagination',
    'bootstrap3',
    'formtools',
    # "registration_defaults",
    "sass_processor",
    "images",
    'candidator',
    'taggit',
    'haystack',
    'elections',
    'popolo',
    'markdown_deux',
    'django_extensions',
    #'social_django',
    'sorl.thumbnail',
    'django.contrib.admin',
    'tinymce',
    'mathfilters',
    'newsletter',
    'rest_framework',
    'preguntales',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'popular_proposal',
    'backend_staff',
    'backend_citizen',
    'backend_candidate',
    'django_filters',
    'django_ogp',
    'debug_toolbar',
    # 'debug_panel',
    'constance',
)
INSTALLED_APPS_AFTER_ALL = ('el_pagination',)


# REGISTRATION
ACCOUNT_ACTIVATION_DAYS = 7
LOGIN_REDIRECT_URL = 'backend_citizen:index'

# SOCIAL AUTH
SOCIAL_AUTH_LOGIN_REDIRECT_URL = LOGIN_REDIRECT_URL

AUTHENTICATION_BACKENDS = (
    'social.backends.facebook.FacebookOAuth2',
    'social.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

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
SOCIAL_AUTH_PIPELINE = (
        'social.pipeline.social_auth.social_details',
        'social.pipeline.social_auth.social_uid',
        'social.pipeline.social_auth.auth_allowed',
        'social.pipeline.social_auth.social_user',
        'social.pipeline.user.get_username',
        'social.pipeline.user.create_user',
        'social.pipeline.social_auth.associate_by_email',  # <--- enable this one
        'social.pipeline.social_auth.associate_user',
        'social.pipeline.social_auth.load_extra_data',
        'social.pipeline.user.user_details',
)

SASS_PROCESSOR_ENABLED = True
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'sass_processor.finders.CssFinder',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'linaro_django_pagination.middleware.PaginationMiddleware',
    'social.apps.django_app.middleware.SocialAuthExceptionMiddleware',
)


# SITE_ID
SITE_ID = 1
NEWSLETTER_CONFIRM_EMAIL = False
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

LANGUAGE_CODE = 'es-cl'

TIME_ZONE = 'UTC'
# Using django-tinymce
# NEWSLETTER_RICHTEXT_WIDGET = "tinymce.widgets.TinyMCE"

# Send YoQuieroSaber_Juego mails to Cuttlefish (see http://cuttlefish.io)
EMAIL_HOST = 'cuttlefish.oaf.org.au'
EMAIL_PORT = 2525
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = True


THUMBNAIL_DEBUG = False

# CANDIDEITORG API THINGS

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
# CELERY STUFF
BROKER_URL = 'amqp://guest:guest@localhost:5672/'
CELERY_ALWAYS_EAGER = True

CELERYBEAT_SCHEDULE = {'sending-mails-every-2-minutes': {'task': 'preguntales.tasks.send_mails',
                                                         'schedule': timedelta(minutes=2),
                                                         },
                       # 'letting-candidates-know-about-us-every-two-days':
                       # {'task': 'backend_candidate.tasks.send_candidates_their_username_and_password',
                       #                                                     'schedule': timedelta(days=2),
                       #                                                     },
                       }

CELERY_TIMEZONE = 'UTC'
# django tinyMCE
TINYMCE_JS_URL = os.path.join(settings.STATIC_URL, 'js/tiny_mce/tiny_mce.js')
TINYMCE_JS_ROOT = os.path.join(settings.STATIC_URL, 'js/tiny_mce')
TINYMCE_DEFAULT_CONFIG = {
    'plugins': "table,spellchecker,paste,searchreplace",
    'theme': "advanced",
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 10,
}
# Django nose
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
if TESTING:

    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
            'URL': 'http://127.0.0.1:9200/',
            'INDEX_NAME': 'votainteligente_test',
        },
    }
else:
    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
            'URL': 'http://127.0.0.1:9200/',
            'INDEX_NAME': 'votainteligente',
        },
    }

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


# PROPOSALS_ENABLED = True

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

NEW_ANSWER_ENDPOINT = 'NEW_ANSWER_ENDPOINT'

THEME = None


WHEN_TO_NOTIFY = [25, 50, 100, 150, 200]
NOTIFY_CANDIDATES = True
NOTIFY_CANDIDATES_OF_NEW_PROPOSAL = True
NO_REPLY_MAIL = "no-reply@localhost"
EMAIL_LOCALPART = 'municipales2016'
EMAIL_DOMAIN = 'votainteligente.cl'
MAX_AMOUNT_OF_MAILS_TO_CANDIDATE = 3

# HIDDEN_AREAS = ['fundacion-ciudadano-inteligente', ]



class DisableMigrations(object):
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


class Runner(NoseTestSuiteRunner):
    def run_tests(self, test_labels, extra_tests=None):
        settings.MIGRATION_MODULES = DisableMigrations()
        super(Runner, self).run_tests(test_labels, extra_tests=extra_tests)


DONT_USE_MIGRATIONS = 'DONT_USE_MIGRATIONS' in os.environ.keys() and os.environ['DONT_USE_MIGRATIONS'] == '1'

if DONT_USE_MIGRATIONS:
    TEST_RUNNER = 'votainteligente.votainteligente_settings.Runner'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
FACEBOOK_ACCESS_TOKEN = 'FieraEsLaMejorAmigaDeTodos'

# TWITTER_TOKEN = 'TWITTER_TOKEN'
# TWITTER_TOKEN_KEY = 'TWITTER_TOKEN_KEY'
# TWITTER_CON_KEY = 'TWITTER_CON_KEY'
# TWITTER_CON_SECRET_KEY = 'TWITTER_CON_SECRET_KEY'


MARKED_AREAS = ['teodoro-schmidt-9117','cunco-9103','lumaco-9207','melipeuco-9110','gorbea-9107','arica-15101','copiapo-3101','freirina-3303','caldera-3102','tortel-11303','guaitecas-11203','cisnes-11202','rio-ibanez-11402','santa-barbara-8311','contulmo-8204','alto-biobio-8314','treguaco-8420','los-alamos-8206','hualpen-8112','lota-8106','monte-patria-4303','los-vilos-4203','rio-hurtado-4305','la-higuera-4104','frutillar-10105','maullin-10108','castro-10201','puqueldon-10206','puyehue-10304','san-juan-de-la-costa-10306','puerto-montt-10101','corral-14102','futrono-14202','paillaco-14107','lago-ranco-14203','valdivia-14101','rauco-7305','rio-claro-7108','hualane-7302','san-clemente-7109','longavi-7403','talca-7101','constitucion-7102','coltauco-6104','machali-6108','paredones-6206','peralillo-6307','rengo-6115','quilicura-13125','curacavi-13503','independencia-13108','san-bernardo-13401','puente-alto-13201','penaflor-13605','pedro-aguirre-cerda-13121','huechuraba-13107','alto-hospicio-1107','san-antonio-5601','santa-maria-5706','llaillay-5703']

CONSTANCE_CONFIG = {
    'SOUL_MATE_INFO_ABOUT_CANDIDATES_MINUTES':(10,'Duracion cache media naranja'),
    'INFINITE_CACHE':(1440,'Tiempo Cache'),
    'PROPOSALS_ENABLED' : (True, 'Habilitar propuestas'),
    'WHEN_TO_NOTIFY': ('25, 50, 100, 150, 200', 'Cuando notificar'),
    'NOTIFY_CANDIDATES': (True, 'Notificar a los candidatos'),
    'NOTIFY_CANDIDATES_OF_NEW_PROPOSAL': (True, 'Notificar a los candidatos por una nueva propuesta'),
    'NO_REPLY_MAIL': ("no-reply@localhost", 'Cuenta email de envio de correos'),
    'EMAIL_LOCALPART': ("municipales2016", 'Cuenta email localhost'),
    'EMAIL_DOMAIN': ("votainteligente.cl", 'Nombre dominio'),
    'MAX_AMOUNT_OF_MAILS_TO_CANDIDATE': (3, 'Numero maximo de envios de emails a candidatos'),
    'TWITTER_TOKEN': ('', 'Twitter token'),
    'MARKED_AREAS': (MARKED_AREAS, u'Areas que tienen alguna marca'),
    'TWITTER_TOKEN_KEY': ('', 'Twitter token key'),
    'TWITTER_CON_KEY': ('', 'Twitter connection key'),
    'TWITTER_CON_SECRET_KEY': ('', 'Twitter connection secret key'),
    'HIDDEN_AREAS': ('fundacion-ciudadano-inteligente', 'Seccion oculta'),
    'NAV_BAR': ('profiles, questionary, soulmate, facetoface, ask, ranking', 'Menu de navegacion'),
    'WEBSITE_METADATA_AUTHOR': ('', 'Nombre del autor'),
    'WEBSITE_METADATA_DESCRIPTION': ('', 'Descripcion del sitio'),
    'WEBSITE_METADATA_KEYWORD': ('', 'Palabras claves del sitio'),
    'WEBSITE_OGP_TITLE': ('VotaInteligente', 'Titulo OGP'),
    'WEBSITE_OGP_TYPE': ('website', 'Tipo OGP'),
    'WEBSITE_OGP_URL': ('https://www.mi-domain.org/', 'URL base OGP'),
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
}

try:
    from local_settings import *
except ImportError, e:
    pass
