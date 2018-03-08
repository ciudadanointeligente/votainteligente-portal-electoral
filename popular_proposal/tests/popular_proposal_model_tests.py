# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase
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


class PopularProposalTestCase(ProposingCycleTestCaseBase):
    def setUp(self):
        super(PopularProposalTestCase, self).setUp()

    def test_instantiate_one(self):
        popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                          data=self.data,
                                                          title=u'This is a title',
                                                          clasification=u'education'
                                                          )
        self.assertTrue(popular_proposal.created)
        self.assertTrue(popular_proposal.updated)
        self.assertTrue(popular_proposal.slug)
        self.assertEquals(popular_proposal.title, u'This is a title')
        self.assertIn(popular_proposal, self.fiera.popularproposals.all())
        self.assertIsNone(popular_proposal.temporary)
        self.assertFalse(popular_proposal.background)
        self.assertFalse(popular_proposal.contact_details)
        self.assertFalse(popular_proposal.document)
        self.assertFalse(popular_proposal.image)
        self.assertEquals(popular_proposal.clasification, u'education')
        self.assertFalse(popular_proposal.is_local_meeting)
        self.assertFalse(popular_proposal.is_reported)
        self.assertFalse(popular_proposal.featured)
        content_type = popular_proposal.content_type
        expected_content_type = ContentType.objects.get_for_model(PopularProposal)
        self.assertEquals(content_type, expected_content_type)
        self.assertFalse(popular_proposal.summary)
        self.assertFalse(popular_proposal.important_within_organization)
        self.assertEquals(popular_proposal.one_liner, "")

    def test_popular_proposal_card_as_property(self):
        popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                          data=self.data,
                                                          title=u'This is a title',
                                                          clasification=u'education'
                                                          )
        expected_card_html =  get_template("popular_proposal/popular_proposal_card.html").render({
            'proposal': popular_proposal
        })

        self.assertEquals(popular_proposal.card, expected_card_html)

    def test_get_classification_text(self):
        popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                       data=self.data,
                                                       title=u'This is a title',
                                                       clasification=TOPIC_CHOICES[1][0]
                                                       )
        self.assertEquals(popular_proposal.get_classification(), TOPIC_CHOICES[1][1])
        popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                       data=self.data,
                                                       title=u'This is a title',
                                                       clasification="perrito"
                                                       )
        self.assertEquals(popular_proposal.get_classification(), u"")

    def test_reportedproposals_are_not_in_default_manager(self):
        p1 = PopularProposal.objects.create(proposer=self.fiera,
                                            data=self.data,
                                            title=u'This is a title',
                                            clasification=u'education'
                                            )
        p2 = PopularProposal.objects.create(proposer=self.fiera,
                                            data=self.data,
                                            title=u'This is a title',
                                            clasification=u'education',
                                            is_reported=True
                                            )
        self.assertIn(p1, PopularProposal.objects.all())
        self.assertNotIn(p2, PopularProposal.objects.all())
        # now ordered
        self.assertIn(p1, PopularProposal.ordered.all())
        self.assertNotIn(p2, PopularProposal.ordered.all())
        #but they appear in the all Manager
        self.assertIn(p1, PopularProposal.all_objects.all())
        self.assertIn(p2, PopularProposal.all_objects.all())

    def test_featured_proposals_are_first(self):
        p1 = PopularProposal.objects.create(proposer=self.fiera,
                                            data=self.data,
                                            title=u'This is a title1',
                                            clasification=u'education'
                                            )
        p2 = PopularProposal.objects.create(proposer=self.fiera,
                                            data=self.data,
                                            title=u'This is a title2',
                                            clasification=u'education',
                                            featured=True
                                            )
        p3 = PopularProposal.objects.create(proposer=self.fiera,
                                            data=self.data,
                                            title=u'This is a title3',
                                            clasification=u'education'
                                            )
        proposals = PopularProposal.objects.all()
        self.assertEquals(p2, proposals.first())

    def test_home_view_brings_featured_first(self):
        p1 = PopularProposal.objects.create(proposer=self.fiera,
                                            data=self.data,
                                            title=u'This is a title1',
                                            clasification=u'education'
                                            )
        p2 = PopularProposal.objects.create(proposer=self.fiera,
                                            data=self.data,
                                            title=u'This is a title2',
                                            clasification=u'education',
                                            featured=True
                                            )
        p3 = PopularProposal.objects.create(proposer=self.fiera,
                                            data=self.data,
                                            title=u'This is a title3',
                                            clasification=u'education',
                                            featured=True
                                            )
        url = reverse('home')
        response = self.client.get(url)
        featured_proposals = response.context['featured_proposals']
        # this proposal has 4 likes
        self.assertIn(p2, featured_proposals)
        self.assertIn(p3, featured_proposals)
        self.assertNotIn(p1, featured_proposals)

    def test_get_ribbon_text(self):
        p1 = PopularProposal.objects.create(proposer=self.fiera,
                                            data=self.data,
                                            title=u'This is a title1',
                                            clasification=u'education'
                                            )
        self.assertFalse(p1.ribbon_text)
        p1.is_local_meeting = True
        self.assertTrue(p1.ribbon_text)


    @override_settings(EXCLUDED_PROPOSALS_APPS=["sites" ,])
    def test_proposals_exclude_certain_types_of_proposals(self):
        p1 = PopularProposal.objects.create(proposer=self.fiera,
                                            data=self.data,
                                            title=u'This is a title1',
                                            clasification=u'education'
                                            )
        p2 = PopularProposal.objects.create(proposer=self.fiera,
                                            data=self.data,
                                            title=u'This is a title2',
                                            clasification=u'education',
                                            featured=True
                                            )
        p3 = PopularProposal.objects.create(proposer=self.fiera,
                                            data=self.data,
                                            title=u'This is a title3',
                                            clasification=u'education'
                                            )
        something_else = ContentType.objects.get_for_model(Site)
        p3.content_type = something_else
        p3.save()
        proposals = PopularProposal.objects.all()
        self.assertNotIn(p3, proposals)


    def test_generate_og_image(self):
        popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                          data=self.data,
                                                          title=u'This is a title',
                                                          clasification=u'education'
                                                          )
        self.assertTrue(popular_proposal.generate_og_image())

    def test_create_popular_proposal_from_temporary_data(self):

        data = self.data
        data["join_advocacy_url"] = u"http://whatsapp.com/somegroup"
        # Testing
        temporary_data = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                              data=self.data)
        original_amount_of_mails = len(mail.outbox)
        popular_proposal = temporary_data.create_proposal(moderator=self.feli)
        self.assertEquals(popular_proposal.proposer, self.fiera)
        popular_proposal = PopularProposal.objects.get(id=popular_proposal.id)
        self.assertEquals(popular_proposal.join_advocacy_url, u"http://whatsapp.com/somegroup")
        self.assertEquals(popular_proposal.clasification, data['clasification'])
        self.assertEquals(popular_proposal.data, self.data)
        self.assertEquals(popular_proposal.title, self.data['title'])
        temporary_data = ProposalTemporaryData.objects.get(id=temporary_data.id)
        self.assertEquals(temporary_data.created_proposal, popular_proposal)
        self.assertEquals(temporary_data.status, ProposalTemporaryData.Statuses.Accepted)
        # There was a mail sent to Fiera because
        # her proposal was accepted
        self.assertEquals(len(mail.outbox), 1)
        the_mail = mail.outbox[0]
        self.assertIn(self.fiera.email, the_mail.to)
        self.assertEquals(len(the_mail.to), original_amount_of_mails + 1)

    def test_proposal_has_supporting_organizations(self):
        popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                          data=self.data,
                                                          title=u'This is a title'
                                                          )
        supporting_org = User.objects.create(username='organizacionorganizada',
                                             email='oo@organizaciones.org',
                                             password='PASSWORD')
        supporting_org.profile.is_organization = True
        supporting_org.profile.save()
        support = ProposalLike.objects.create(user=supporting_org,
                                           proposal=popular_proposal)

        supporting_org2 = User.objects.create(username='organizacionorganizada2',
                                             email='o1o2@organizaciones.org',
                                             password='PASSWORD')
        supporting_org2.profile.is_organization = True
        supporting_org2.profile.save()

        support2 = ProposalLike.objects.create(user=supporting_org2,
                                           proposal=popular_proposal)

        ## Hay dos organizaciones que le ponen support a esta propuesta
        ## y yo quiero poder hacer que esten en alguna parte listadas

        ProposalLike.objects.create(user=self.feli,
                                    proposal=popular_proposal)

        self.assertIn(supporting_org, popular_proposal.sponsoring_orgs.all())
        self.assertIn(supporting_org2, popular_proposal.sponsoring_orgs.all())
        self.assertEquals(popular_proposal.sponsoring_orgs.count(), 2)

    def test_render_proposal_detail(self):
        popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                          data=self.data,
                                                          title=u'This is a title'
                                                          )
        expected_detail_html =  get_template("popular_proposal/plantillas/detalle_propuesta.html").render({
            'popular_proposal': popular_proposal
        })

        self.assertEquals(popular_proposal.detail_as_html, expected_detail_html)

    def test_get_oneliner(self):
        popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                          data=self.data,
                                                          title=u'This is a title'
                                                          )
        self.assertEquals(popular_proposal.get_one_liner(), popular_proposal.title)
        popular_proposal.one_liner = "one_liner"
        self.assertEquals(popular_proposal.get_one_liner(), popular_proposal.one_liner)
