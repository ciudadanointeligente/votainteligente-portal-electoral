# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase
from backend_citizen.models import Organization, Enrollment
from elections.models import Area
from django.contrib.auth.models import User
from popular_proposal.models import ProposalTemporaryData, PopularProposal, ProposalLike
from popular_proposal.tests.wizard_tests import WizardDataMixin
from django.core import mail
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.template.loader import get_template
from django.contrib.sites.models import Site
from django.test import override_settings
from votita.models import KidsProposal, KidsGathering
from django.core.urlresolvers import reverse
from votita.forms.forms import wizard_forms_fields
from constance.test import override_config


USER_PASSWORD = 'secr3t'


class PopularProposalTestCase(ProposingCycleTestCaseBase):
    def setUp(self):
        super(PopularProposalTestCase, self).setUp()
        # Enrolling Fiera with the organization
        self.org = Organization.objects.create(name=u'La Cosa Nostra')
        self.enrollment = Enrollment.objects.create(organization=self.org,
                                                    user=self.fiera)

    def test_instantiate_one(self):
        popular_proposal = KidsProposal.objects.create(proposer=self.fiera,
                                                       area=self.arica,
                                                       data=self.data,
                                                       title=u'This is a title',
                                                       clasification=u'education'
                                                       )
        self.assertIsInstance(popular_proposal, PopularProposal)
        self.assertTrue(popular_proposal.is_kids)

    def test_card(self):
        kids_proposal = KidsProposal.objects.create(proposer=self.fiera,
                                                    area=self.arica,
                                                    data=self.data,
                                                    title=u'Kids!!',
                                                    clasification=u'education'
                                                    )
        expected_card_html =  get_template("votita/card.html").render({
            'proposal': kids_proposal
        })
        popular_proposal = PopularProposal.ordered.get(id=kids_proposal.id)
        self.assertEquals(popular_proposal.card, expected_card_html)

    def test_listing_all_proposals(self):
        url = reverse('popular_proposals:home')
        kids_proposal = KidsProposal.objects.create(proposer=self.fiera,
                                                    area=self.arica,
                                                    data=self.data,
                                                    title=u'Kids!!',
                                                    clasification=u'education'
                                                    )
        response = self.client.get(url)
        self.assertIn(kids_proposal, response.context['popular_proposals'])
        proposal_again = response.context['popular_proposals'].get(id=kids_proposal.id)
        self.assertIsInstance(proposal_again, KidsProposal)


class KidsGatheringTestCase(ProposingCycleTestCaseBase):
    def setUp(self):
        super(KidsGatheringTestCase, self).setUp()

    def test_instanciate_model(self):
        stats_data = {
            'male': 10,
            'female': 10,
            'others': 10
        }
        gathering = KidsGathering.objects.create(name=u"Título",
                                                 stats_data=stats_data,
                                                 presidents_features=['ingeligente',
                                                                      'honesto'])
        self.assertTrue(gathering.created)
        self.assertTrue(gathering.updated)

    def test_a_proposal_is_related_to_it(self):
        stats_data = {
            'male': 10,
            'female': 10,
            'others': 10
        }
        gathering = KidsGathering.objects.create(name=u"Título",
                                                 stats_data=stats_data)
        kids_proposal = KidsProposal.objects.create(proposer=self.fiera,
                                                    area=self.arica,
                                                    gathering=gathering,
                                                    data=self.data,
                                                    title=u'Kids!!',
                                                    clasification=u'education'
                                                    )
        self.assertIn(kids_proposal, gathering.proposals.all())

@override_config(DEFAULT_AREA='argentina')
class VotitaWizardTestCase(ProposingCycleTestCaseBase, WizardDataMixin):
    url = reverse('votita:create_proposal')
    wizard_forms_fields =  wizard_forms_fields
    def setUp(self):
        super(VotitaWizardTestCase, self).setUp()
        self.example_data = self.get_example_data_for_post()
        self.feli = User.objects.get(username='feli')
        self.feli.set_password(USER_PASSWORD)
        self.feli.save()

    def test_create_a_proposal(self):
        argentina = Area.objects.create(name=u'Argentina', id='argentina')
        original_amount = len(mail.outbox)
        response = self.fill_the_whole_wizard(default_view_slug='votita_wizard',)
        temporary_data = response.context['popular_proposal']
        temporary_data = ProposalTemporaryData.objects.get(id=temporary_data.id)
        self.assertTrue(temporary_data.created_proposal)


@override_config(DEFAULT_AREA='argentina')
class VotitaWizardInsideAGathering(ProposingCycleTestCaseBase, WizardDataMixin):
    wizard_forms_fields =  wizard_forms_fields
    def setUp(self):
        argentina = Area.objects.create(name=u'Argentina', id='argentina')
        self.example_data = self.get_example_data_for_post()
        self.feli = User.objects.get(username='feli')
        self.feli.set_password(USER_PASSWORD)
        self.feli.save()
        stats_data = {
            'male': 10,
            'female': 10,
            'others': 10
        }
        self.gathering = KidsGathering.objects.create(name=u"Título",
                                                      stats_data=stats_data)
        self.url = reverse('votita:create_proposal_for_gathering_wizard',
                           kwargs={'pk':self.gathering.id})

    def test_create_a_proposal_with_a_gathering(self):
        response = self.fill_the_whole_wizard(default_view_slug='votita_wizard',)
        temporary_data = response.context['popular_proposal']
        self.assertTrue(temporary_data.created_proposal)
