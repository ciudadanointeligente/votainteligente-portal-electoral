# coding=utf-8
import sys
import os
import djcelery
from django.conf import settings
djcelery.setup_loader()
from datetime import timedelta

DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEFAULT_CANDIDATE_EXTRA_INFO = {
    "portrait_photo": "http://votainteligente.cl/static/img/candidate-default.jpg",
    'custom_ribbon': 'ribbon text'
}
DEFAULT_ELECTION_EXTRA_INFO = {
    "extra": "Extra extra extra"
}

TESTING = 'test' in sys.argv
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.flatpages',
    'djcelery',
    'django_nose',
    'django.contrib.sitemaps',
    'candidator',
    'taggit',
    'haystack',
    'elections',
    'popolo',
    'markdown_deux',
    'django_extensions',
    'pagination',
    'sorl.thumbnail',
    'django_admin_bootstrapped',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    'tinymce',
    'mathfilters',
    'newsletter',
    'rest_framework',
    'popolorest',
    'writeit',
    # Uncomment the next line to enable admin documentation:
    #'django.contrib.admindocs',
)

#SITE_ID
SITE_ID = 1
NEWSLETTER_CONFIRM_EMAIL = False
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

# Using django-tinymce
#NEWSLETTER_RICHTEXT_WIDGET = "tinymce.widgets.TinyMCE"

# Send YoQuieroSaber_Juego mails to Cuttlefish (see http://cuttlefish.io)
EMAIL_HOST = 'cuttlefish.oaf.org.au'
EMAIL_PORT = 2525
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = True


THUMBNAIL_DEBUG = True

### CANDIDEITORG API THINGS

CANDIDEITORG_URL = 'http://localhost:3002/api/v2/'
CANDIDEITORG_USERNAME = 'admin'
CANDIDEITORG_API_KEY = 'a'

### CANDIDEITORG API THINGS

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
#CELERY STUFF
BROKER_URL = 'amqp://guest:guest@localhost:5672/'
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
CELERY_ALWAYS_EAGER = True

CELERYBEAT_SCHEDULE = {
        'pushing-to-writeit-every-2-minutes': {
            'task': 'elections.tasks.send_mails_using_writeit',
                    'schedule': timedelta(minutes=2),
                },
}

CELERY_TIMEZONE = 'UTC'


#django tinyMCE
TINYMCE_JS_URL = os.path.join(settings.STATIC_URL, 'js/tiny_mce/tiny_mce.js')
TINYMCE_JS_ROOT = os.path.join(settings.STATIC_URL, 'js/tiny_mce')
TINYMCE_DEFAULT_CONFIG = {
    'plugins': "table,spellchecker,paste,searchreplace",
    'theme': "advanced",
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 10,
}
#Django nose
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

#navigation bar
# NAV_BAR = ('profiles','questionary','soulmate','facetoface','ask','ranking')
NAV_BAR = ('profiles', 'questionary', 'soulmate', 'facetoface', 'ask', 'ranking')
WEBSITE_METADATA = {
    'author': u'Name of the author',
    'description': u'A description for the site',
    'keywords': u'some,tags,separated,by,comma'
}
#for Facebook OGP http://ogp.me/
WEBSITE_OGP = {
    'title': u'Title page for Facebook OGP',
    'type': 'website',
    'url': 'http://www.mi-domain.org/',
    'image': 'img/votai-196.png'
}
#disqus setting dev
WEBSITE_DISQUS = {
    'enabled': True,
    'shortname': 'shortname_disqus',
    'dev_mode': 0
}
#google analytics
WEBSITE_GA = {
    'code': 'UA-XXXXX-X',
    'name': 'ga_name',
    'gsite-verification': 'BCyMskdezWX8ObDCMsm_1zIQAayxYzEGbLve8MJmxHk'
}
#imgur
WEBSITE_IMGUR = {
    #  example client_id, only works with 50 pic a day
    'client_id': 'eb18642b5b220484864483b8e21386c3',
}
#settings for global site
WEBSITE_GENERAL_SETTINGS = {
    'home_title': 'Lorem ipsum dolor sit amet, consectetur adipisicing elit.'
}
#twitter sepparated by comma, eg: votainteligente,votainformado,othertag
WEBSITE_TWITTER = {
    'hashtags': 'votainteligente'
}
CACHE_MINUTES = 0
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

#LOGGING
LOGGING = {'version': 1,
           'disable_existing_loggers': True,
           'formatters': {'simple': {'format': '%(asctime)s %(levelname)s %(message)s'}},
           'handlers': {'console': {'level': 'DEBUG', 'class': 'logging.StreamHandler', 'formatter': 'simple'},
                        'null': {'level': 'DEBUG',
                                 'class': 'logging.NullHandler',
                                 },
                        },
           'loggers': {'django.db.backends': {'level': 'DEBUG', 'handlers': ['null'], 'propagate': False}}
           }
#END LOGGING

WRITEIT_NAME = 'votainteligente'
INSTANCE_URL = "/api/v1/instance/<THE_INSTANCE_ID>/"
WRITEIT_ENDPOINT = 'http://writeit.ciudadanointeligente.org'
WRITEIT_USERNAME = '<YOUR_USERNAME>'
WRITEIT_KEY = '<YOUR_API_KEY>'
NEW_ANSWER_ENDPOINT = 'NEW_ANSWER_ENDPOINT'

THEME = None


#Testing without migrations
from django.conf import settings
from django_nose import NoseTestSuiteRunner


class DisableMigrations(object):
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return "notmigrations"


class Runner(NoseTestSuiteRunner):
    def run_tests(self, test_labels, extra_tests=None):
        settings.MIGRATION_MODULES = DisableMigrations()
        super(Runner, self).run_tests(test_labels, extra_tests=extra_tests)


DONT_USE_MIGRATIONS = 'DONT_USE_MIGRATIONS' in os.environ.keys() and os.environ['DONT_USE_MIGRATIONS'] == '1'

if DONT_USE_MIGRATIONS:
    TEST_RUNNER = 'votainteligente.votainteligente_settings.Runner'


try:
    from local_settings import *
except ImportError, e:
    pass
