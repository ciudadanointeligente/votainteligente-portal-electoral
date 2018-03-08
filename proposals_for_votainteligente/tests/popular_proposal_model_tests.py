# coding=utf-8
from proposals_for_votainteligente.tests import VIProposingCycleTestCaseBase
from elections.models import Area
from django.contrib.auth.models import User
from popular_proposal.models import ProposalTemporaryData, PopularProposal, ProposalLike
from popular_proposal.forms.form_texts import TOPIC_CHOICES
from django.core import mail
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.template.loader import get_template
from django.contrib.sites.models import Site
from django.test import override_settings
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse


class PopularProposalTestCase(VIProposingCycleTestCaseBase):
    def setUp(self):
        super(PopularProposalTestCase, self).setUp()

    def test_instantiate_one(self):
        popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                          area=self.arica,
                                                          data=self.data,
                                                          title=u'This is a title',
                                                          clasification=u'education'
                                                          )
        
        self.assertFalse(popular_proposal.for_all_areas)
        self.assertIn(popular_proposal, self.arica.popularproposals.all())

    def test_proposal_ogp(self):
        site = Site.objects.get_current()
        popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                          area=self.arica,
                                                          data=self.data,
                                                          title=u'This is a title',
                                                          clasification=u'education'
                                                          )
        self.assertTrue(popular_proposal.ogp_enabled)
        self.assertTrue(popular_proposal.ogp_title())
        self.assertEquals('website', popular_proposal.ogp_type())
        expected_url = "http://%s%s" % (site.domain,
                                        popular_proposal.get_absolute_url())
        self.assertEquals(expected_url, popular_proposal.ogp_url())
        self.assertTrue(popular_proposal.ogp_image())

    def test_create_popular_proposal_from_temporary_data(self):

        data = self.data
        data["join_advocacy_url"] = u"http://whatsapp.com/somegroup"
        # Testing
        temporary_data = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                              area=self.arica,
                                                              data=self.data)
        popular_proposal = temporary_data.create_proposal(moderator=self.feli)
        self.assertEquals(popular_proposal.area, self.arica)

    def test_proposal_has_where_was_generated(self):
        a_comuna = Area.objects.filter(classification='Comuna').first()
        popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                          area=self.arica,
                                                          data=self.data,
                                                          generated_at=a_comuna,
                                                          title=u'This is a title',
                                                          clasification=u'education'
                                                          )
        self.assertTrue(popular_proposal)