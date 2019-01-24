# coding=utf-8
import os
import sys
from datetime import timedelta
import imp
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '18_bfrslfj^(m1+k+ks3q@f08rsod46lr0k0=p7+=3z5&cl7gj'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

SITE_ID = 1

# Application definition

INSTALLED_APPS = (
    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'collectfast',
    'django.contrib.staticfiles',
    'django.contrib.flatpages',
    'test_without_migrations',
    'constance',
    'constance.backends.database',
    'django_nose',
    'django.contrib.sitemaps',
    'linaro_django_pagination',
    'bootstrap3',
    'bootstrap4',
    'formtools',
    'robots',
    # "registration_defaults",
    'multiselectfield',
    "sass_processor",
    "images",
    'candidator',
    'taggit',
    'haystack',
    'popolo',
    'elections',
    'votai_utils',
    'markdown_deux',
    'django_extensions',
    'social_django',
    'sorl.thumbnail',
    'django.contrib.admin',
    'tinymce',
    'mathfilters',
    'newsletter',
    'rest_framework',
    'preguntales',
    'votita',
    'suggestions_for_candidates',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'popular_proposal',
    'backend_staff',
    'backend_citizen',
    'backend_candidate',
    'organization_profiles',
    'django_filters',
    'django_ogp',
    'debug_toolbar',
    'agenda',
    'medianaranja2',
    'merepresenta',
    # 'debug_panel',
    'el_pagination',
    'proposal_subscriptions',
    'custom_sites',
    'votai_general_theme',
    'hitcount',

)
INSTALLED_APPS_AFTER_ALL = ()



SOCIAL_AUTH_REDIRECT_IS_HTTPS = True
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

SASS_PROCESSOR_ENABLED = True
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'sass_processor.finders.CssFinder',
)

## Funciona el de arriba??? no tengo callampa idea!!
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'custom_sites.middleware.VotaIcurrentSiteMiddleware',
    # 'linaro_django_pagination.middleware.PaginationMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
]
ALLOWED_HOSTS = ['*']
INTERNAL_IPS = ["127.0.0.1", "localhost"]
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            'votai_general_theme/templates'
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'constance.context_processors.config',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                #'django.template.loaders.app_directories.Loader',
            ],
        },
    },
]
CONSTANCE_ADDITIONAL_FIELDS = {
    'proposals_getter_for_12_n': ['django.forms.fields.ChoiceField', {
        'widget': 'django.forms.Select',
        'choices': (("getter", "por corazones"), ("reading_group", "grupos de lectura"))
    }],
}
NO_REPLY_MAIL = "no-reply@localhost"
EMAIL_LOCALPART = 'municipales2016'
EMAIL_DOMAIN = 'votainteligente.cl'
FACEBOOK_ACCESS_TOKEN = 'FieraEsLaMejorAmigaDeTodos'
CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'
CONSTANCE_CONFIG = {
    'SOUL_MATE_INFO_ABOUT_CANDIDATES_MINUTES':(0,'Duracion cache media naranja'),
    'ORGANIZATIONS_MUST_AGREE_TAC_ON_REGISTER':(False,'Organizaciones deben tener terminos y condiciones al registrarse?'),
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
    'MAILCHIMP_U': ('perrito', 'MAILCHIMP u la partecita u del mailchimp'),
    'MAILCHIMP_ID': ('gatito', 'MAILCHIMP u la partecita u del mailchimp'),
    'MARKED_AREAS': ("", u'Areas que tienen alguna marca'),
    'CANDIDATE_ABSOLUTE_URL_USING_AREA': (True, u'para ver el perfil de los candidatos utilziamos el territorio o utilizamos la elección a la que pertenece?'),
    'TWITTER_TOKEN_KEY': ('', 'Twitter token key'),
    'MENU_CIUDADANO_EN_DROPDOWN': (False, u'El menú ciudadano va en el dropdown menu que está arriba en la derecha?'),
    'TWITTER_CON_KEY': ('', 'Twitter connection key'),
    'TWITTER_CON_SECRET_KEY': ('', 'Twitter connection secret key'),
    'HIDDEN_AREAS': ('', 'Seccion oculta'),
    'DEFAULT_ELECTION_ID': (1, u'La elección que aparece en /candidaturas'),
    'NAV_BAR': ('profiles, questionary, soulmate, facetoface, ask, ranking', 'Menu de navegacion'),
    'NAV_BAR_VOTITA_DISPLAYED': (False, 'Desplegamos el navbar del votita??????'),
    'SHOW_RIBBON_IN_CANDIDATE': (False, u"Debería aparecerles la franja roja que dice 'No se ha compormetido?'"),
    'SHOW_ALL_CANDIDATES_IN_THIS_ORDER': ("", u"Mostrar todos los candidatos en la parte de /candidatos? "),
    'CAN_CREATE_TEST_PROPOSAL': (False, u'Se pueden crear propuestas de prueba?'),
    'SEARCH_SUBSCRIPTION_ENABLED': (True, u'Suscribirse a una búsqueda está habilitado? esto sólo esconde los links.'),
    'WEBSITE_METADATA_AUTHOR': ('', 'Nombre del autor'),
    'PERIODIC_REPORTS_ENABLED': (False, u'Están habilitadas los envíos de reportes periódicos sobre las propuestas?'),
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
    'MEDIA_NARANJA_QUESTIONS_ENABLED': (True, u'Si bajas esto la 1/2 n sólo usará propuestas ciudadanas'),

    'ESTRATEGIA_SELECCION_PROPUESTAS': ("getter", u'Qué estrategia usamos para mostrar propuestas en la 1/2 naranja', 'proposals_getter_for_12_n'),
    'MEREPRESENTA_COLIGACAO_ATENUATION_FACTOR': (1.0, u'o factor de atenuacao de nota de coligacao'),
    'MEREPRESENTA_IDENTITY_MULTIPLICATION_FACTOR': (1.0, u'o factor de multiplicacao de desprivilegio'),
    'MEREPRESENTA_RESULTADO_CANTIDADE': (100, u'o factor de multiplicacao de desprivilegio'),
    'MEREPRESENTA_CANDIDATES_ALLOWED_TO_LOGIN': (True, u'os candidatos podem entrar na plataforma'),
    'DONT_SHOW_AREAS_IN_PROPOSAL_WIZARD': (False, u'No muestres las areas en el wizard de creación de propuestas'),
}
TESTING = 'test' in sys.argv
if TESTING:

    import os
    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
            'PATH': os.path.join(os.path.dirname(__file__),'..', 'whoosh_index'),
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

# SITE_ID
SITE_ID = 1
NEWSLETTER_CONFIRM_EMAIL = False
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

LANGUAGE_CODE = 'es-cl'
SITE_ROOT = os.path.dirname(os.path.realpath(__name__))
LOCALE_PATHS = ( os.path.join(SITE_ROOT, 'locale'), )
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
TEMPLATE_DEBUG = False


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
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'critical.log',
        },
    },

    'loggers': {
        '': {
            'handlers': ['file'],
            'level': 'CRITICAL'
       },

        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'elasticsearch': {
            'handlers': ['file'],
            'level': 'CRITICAL',
            'propagate': True,
       },
        'urllib3': {
            'handlers': ['file'],
            'level': 'CRITICAL',
            'propagate': True,
       },
        'django.security.DisallowedHost': {
            'handlers': ['mail_admins'],
            'level': 'CRITICAL',
            'propagate': False,
        },
    }
}
# Proposals Periodic
# how often proposal reports are sent in days
HOW_OFTEN_PROPOSAL_REPORTS_ARE_SENT = 7

# CELERY STUFF
BROKER_URL = 'amqp://guest:guest@localhost:5672/'
CELERY_ALWAYS_EAGER = False

CELERY_TIMEZONE = 'UTC'
CELERYBEAT_SCHEDULE = {'sending-new-proposals-once-a-day': {'task': 'proposal_subscriptions.tasks.send_new_proposals_to_subscribers',
                                                         'schedule': timedelta(days=1),
                                                         },
                       'new-commitments-notifications': {'task': 'proposal_subscriptions.tasks.send_commitment_notifications',
                                                                                'schedule': timedelta(days=7),
                                                                                },
                       'proposal_periodic_reports': {'task': 'popular_proposal.tasks.report_sender_task',
                                                     'schedule': timedelta(days=HOW_OFTEN_PROPOSAL_REPORTS_ARE_SENT)}
                       # 'letting-candidates-know-about-us-every-two-days':
                       # {'task': 'backend_candidate.tasks.send_candidates_their_username_and_password',
                       #                                                     'schedule': timedelta(days=2),
                       #                                                     },
                       }

# Django nose
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
TEST_WITHOUT_MIGRATIONS_COMMAND = 'django_nose.management.commands.test.Command'

# PROPOSALS_ENABLED = True

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}
CACHE_MINUTES = 0
HEAVY_PAGES_CACHE_MINUTES = 1
NEW_ANSWER_ENDPOINT = 'NEW_ANSWER_ENDPOINT'

REST_FRAMEWORK = {
    # specifying the renderers
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework_csv.renderers.CSVRenderer',
    ),
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 30,
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '10/day',
        'user': '100/day'
    }
}
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# REGISTRATION
ACCOUNT_ACTIVATION_DAYS = 7
LOGIN_REDIRECT_URL = 'backend_citizen:index'

# SOCIAL AUTH
SOCIAL_AUTH_LOGIN_REDIRECT_URL = LOGIN_REDIRECT_URL

AUTHENTICATION_BACKENDS = (
    'social_core.backends.facebook.FacebookOAuth2',
    'social_core.backends.google.GoogleOAuth2',
    'votainteligente.authentication_backend.VotaIAuthenticationBackend',
)
SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
    'social_core.pipeline.social_auth.associate_by_email',
    'backend_citizen.image_getter_from_social.get_image_from_social',
)

ROOT_URLCONF = 'votainteligente.urls'

#TEMPLATES = [
#    {
#        'BACKEND': 'django.template.backends.django.DjangoTemplates',
#        'DIRS': ["votai_general_theme/templates"],
#        'APP_DIRS': True,
#        'OPTIONS': {
#            'context_processors': [
#                'django.template.context_processors.debug',
#                'django.template.context_processors.request',
#                'django.contrib.auth.context_processors.auth',
#                'django.contrib.messages.context_processors.messages',
#            ],
#        },
#    },
#]

WSGI_APPLICATION = 'votainteligente.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL = '/cache/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'cache')

# django tinyMCE
TINYMCE_JS_URL = os.path.join(STATIC_URL, 'js/tiny_mce/tiny_mce.js')
TINYMCE_JS_ROOT = os.path.join(STATIC_URL, 'js/tiny_mce')
TINYMCE_DEFAULT_CONFIG = {
    'plugins': "table,spellchecker,paste,searchreplace",
    'theme': "advanced",
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 10,
}
ORGANIZATION_TEMPLATES_USING_HBS = True
from votainteligente.votainteligente_settings import *

if TESTING:
    from testing_settings import *
else:
    try:
        from local_settings import *
    except ImportError, e:
        pass

if THEME:
    try:
        stand_alone_urls = '%s.stand_alone_urls' % THEME
        imp.find_module(stand_alone_urls)
        ROOT_URLCONF = stand_alone_urls

    except ImportError:
        pass
    try:
        # Esto es un salto al vacio hermano
        # si funciona y todas las plataformas siguen funcionando 
        # estamos al otro litro
        # STATIC_ROOT = os.path.join(BASE_DIR, THEME ,'static')
        STATICFILES_DIRS += [os.path.join(BASE_DIR, THEME ,'static'), ]
        pass
    except:
        pass
    TEMPLATES[0]['DIRS'] = ['%s/templates' % THEME, 'votai_general_theme/templates']
    if THEME not in INSTALLED_APPS:
        INSTALLED_APPS_AFTER_ALL += (THEME, )
INSTALLED_APPS += INSTALLED_APPS_AFTER_ALL
