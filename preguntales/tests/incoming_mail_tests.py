# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from django.test.utils import override_settings
from elections.models import Election, Candidate
from preguntales.models import Message, Answer
from datetime import datetime
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from mock import patch, call
from preguntales.forms import MessageForm


class IncomingTest(TestCase):
    pass
