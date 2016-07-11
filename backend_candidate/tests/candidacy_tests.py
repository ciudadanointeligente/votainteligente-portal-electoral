# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from elections.models import Candidate
from django.contrib.auth.models import User
from popular_proposal.models import ProposalTemporaryData, PopularProposal
from popular_proposal.forms import ProposalForm
from django.core.urlresolvers import reverse
from django.core import mail
from backend_candidate.models import Candidacy, is_candidate
from django.template import Template, Context


class CandidacyModelTestCase(TestCase):
    def setUp(self):
        super(CandidacyModelTestCase, self).setUp()
        self.feli = User.objects.get(username='feli')
        self.feli.set_password('alvarez')
        self.feli.save()
        self.candidate = Candidate.objects.create(name='Candidate')

    def test_instanciate_candidacy(self):
        candidacy = Candidacy.objects.create(user=self.feli,
                                             candidate=self.candidate
                                             )
        self.assertEquals(candidacy.user, self.feli)
        self.assertEquals(candidacy.candidate, self.candidate)
        self.assertTrue(candidacy.created)
        self.assertTrue(candidacy.updated)

    def test_user_has_candidacy(self):
        self.assertFalse(is_candidate(self.feli))
        candidacy = Candidacy.objects.create(user=self.feli,
                                             candidate=self.candidate
                                             )
        self.assertTrue(is_candidate(self.feli))

    def test_filter_times(self):
        template = Template("{% load votainteligente_extras %}{% if user|is_candidate %}Si{% else %}No{% endif %}")
        context = Context({'user': self.feli})
        self.assertEqual(template.render(context), u'No')
        candidacy = Candidacy.objects.create(user=self.feli,
                                             candidate=self.candidate
                                             )
        self.assertEqual(template.render(context), u'Si')

    def test_get_candidate_home(self):
        url = reverse('backend_candidate:home')
        self.client.login(username=self.feli,
                          password='alvarez')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)
        candidacy = Candidacy.objects.create(user=self.feli,
                                             candidate=self.candidate
                                             )
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertIn(candidacy, response.context['candidacies'])
