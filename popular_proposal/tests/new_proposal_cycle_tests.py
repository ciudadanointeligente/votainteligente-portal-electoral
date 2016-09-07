
# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase
from backend_citizen.models import Organization, Enrollment
from django.contrib.auth.models import User
from popular_proposal.models import ProposalTemporaryData, PopularProposal
from popular_proposal.forms import ProposalForm
from django.core.urlresolvers import reverse
from django.core import mail
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.contrib.sites.models import Site


class TemporaryDataForPromise(ProposingCycleTestCaseBase):
    def setUp(self):
        super(TemporaryDataForPromise, self).setUp()

    def test_instanciate_one(self):
        temporary_data = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                              area=self.arica,
                                                              data=self.data)
        self.assertTrue(temporary_data)
        self.assertFalse(temporary_data.rejected)
        self.assertFalse(temporary_data.rejected_reason)

        self.assertIsNotNone(temporary_data.comments['title'])
        self.assertIsNotNone(temporary_data.comments['problem'])
        self.assertIsNotNone(temporary_data.comments['solution'])
        self.assertIsNotNone(temporary_data.comments['when'])
        self.assertIsNotNone(temporary_data.comments['causes'])
        self.assertIsNotNone(temporary_data.created)
        self.assertIsNotNone(temporary_data.updated)
        self.assertIsNotNone(temporary_data.overall_comments)
        self.assertEquals(temporary_data.status, ProposalTemporaryData.Statuses.InOurSide)
        self.assertIn(temporary_data, self.fiera.temporary_proposals.all())
        self.assertEquals(temporary_data.get_title(), self.data['title'])
        self.assertEquals(str(temporary_data.get_title()), self.data['title'])

    def test_send_temporary_data_new_mail(self):
        temporary_data = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                              area=self.arica,
                                                              data=self.data)
        temporary_data.notify_new()
        self.assertEquals(len(mail.outbox), 1)
        the_mail = mail.outbox[0]
        self.assertTrue(the_mail)
        self.assertIn(self.fiera.email, the_mail.to)

    def test_proposing_with_an_organization(self):
        local_org = Organization.objects.create(name="Local Organization")
        temporary_data = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                              organization=local_org,
                                                              area=self.arica,
                                                              data=self.data)
        self.assertTrue(temporary_data)
        self.assertEquals(temporary_data.organization, local_org)

    def test_needing_moderation_proposals(self):
        td_waiting_for_moderation = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                                         area=self.arica,
                                                                         data=self.data)
        td_waiting_for_moderation2 = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                                          area=self.arica,
                                                                          data=self.data)
        needs_citizen_action = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                                    status=ProposalTemporaryData.Statuses.InTheirSide,
                                                                    area=self.arica,
                                                                    data=self.data)
        self.assertIn(td_waiting_for_moderation, ProposalTemporaryData.needing_moderation.all())
        self.assertIn(td_waiting_for_moderation2, ProposalTemporaryData.needing_moderation.all())
        self.assertNotIn(needs_citizen_action, ProposalTemporaryData.needing_moderation.all())

    def test_rejecting_a_proposal(self):
        temporary_data = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                              area=self.arica,
                                                              data=self.data)
        original_amount_of_mails = len(mail.outbox)
        temporary_data.reject('es muy mala la cosa')
        temporary_data = ProposalTemporaryData.objects.get(id=temporary_data.id)
        self.assertEquals(temporary_data.rejected_reason, 'es muy mala la cosa')
        self.assertEquals(temporary_data.status, ProposalTemporaryData.Statuses.Rejected)
        self.assertEquals(len(mail.outbox), original_amount_of_mails + 1)

        the_mail = mail.outbox[0]
        self.assertIn(self.fiera.email, the_mail.to)
        self.assertEquals(len(the_mail.to), 1)
        # context = Context({'area': self.arica,
        #                    'temporary_data': temporary_data,
        #                    'moderator': self.feli
        #                    })
        # template_body = get_template('mails/popular_proposal_rejected_body.html')
        # template_subject = get_template('mails/popular_proposal_rejected_subject.html')
        # template_body.render(context)
        # template_subject.render(context)
        self.assertTrue(the_mail.body)
        self.assertTrue(the_mail.subject)


class ProposingViewTestCase(ProposingCycleTestCaseBase):
    def setUp(self):
        super(ProposingViewTestCase, self).setUp()
        self.feli = User.objects.get(username='feli')
        self.feli.set_password('alvarez')
        self.feli.save()

    def test_get_proposing_view(self):
        url = reverse('popular_proposals:propose', kwargs={'slug': self.arica.id})
        #need to be loggedin
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)

        self.client.login(username=self.feli,
                          password='alvarez')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        form = response.context['form']
        self.assertEquals(self.arica, response.context['area'])
        self.assertIsInstance(form, ProposalForm)

    def test_post_proposing_view(self):
        url = reverse('popular_proposals:propose', kwargs={'slug': self.arica.id})

        self.client.login(username=self.feli,
                          password='alvarez')
        self.assertFalse(ProposalTemporaryData.objects.all())
        response = self.client.post(url, data=self.data, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('popular_proposal/thanks.html')
        temporary_data = ProposalTemporaryData.objects.get()
        self.assertTrue(temporary_data)


class PopularProposalTestCase(ProposingCycleTestCaseBase):
    def setUp(self):
        super(PopularProposalTestCase, self).setUp()
        # Enrolling Fiera with the organization
        self.org = Organization.objects.create(name=u'La Cosa Nostra')
        self.enrollment = Enrollment.objects.create(organization=self.org,
                                                    user=self.fiera)

    def test_instantiate_one(self):
        popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                          area=self.arica,
                                                          data=self.data,
                                                          title=u'This is a title',
                                                          clasification=u'education'
                                                          )
        self.assertTrue(popular_proposal.created)
        self.assertTrue(popular_proposal.updated)
        self.assertTrue(popular_proposal.slug)
        self.assertEquals(popular_proposal.title, u'This is a title')
        self.assertIn(popular_proposal, self.fiera.proposals.all())
        self.assertIn(popular_proposal, self.arica.proposals.all())
        self.assertIsNone(popular_proposal.temporary)
        self.assertFalse(popular_proposal.background)
        self.assertFalse(popular_proposal.contact_details)
        self.assertFalse(popular_proposal.document)
        self.assertFalse(popular_proposal.image)
        self.assertEquals(popular_proposal.clasification, u'education')
        self.assertFalse(popular_proposal.for_all_areas)

    def test_proposal_ogp(self):
        site = Site.objects.get_current()
        popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                          area=self.arica,
                                                          data=self.data,
                                                          title=u'This is a title',
                                                          clasification=u'education'
                                                          )
        self.assertTrue(popular_proposal.ogp_enabled)
        self.assertIn(popular_proposal.title, popular_proposal.ogp_title())
        self.assertEquals('website', popular_proposal.ogp_type())
        expected_url = "http://%s%s" % (site.domain,
                                        popular_proposal.get_absolute_url())
        self.assertEquals(expected_url, popular_proposal.ogp_url())
        expected_url = "http://%s%s" % (site.domain,
                                        static('img/logo_vi_og.jpg'))
        self.assertEquals(expected_url, popular_proposal.ogp_image())

    def test_can_have_an_organization(self):
        popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                          area=self.arica,
                                                          data=self.data,
                                                          organization=self.org,
                                                          title=u'This is a title'
                                                          )

    def test_create_popular_proposal_from_temporary_data(self):

        data = self.data
        data['organization'] = self.org.id
        # Testing
        temporary_data = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                              area=self.arica,
                                                              data=self.data)
        original_amount_of_mails = len(mail.outbox)
        popular_proposal = temporary_data.create_proposal(moderator=self.feli)
        self.assertEquals(popular_proposal.proposer, self.fiera)
        self.assertTrue(popular_proposal.organization)
        self.assertEqual(self.enrollment.user, self.fiera)
        popular_proposal = PopularProposal.objects.get(id=popular_proposal.id)
        self.assertEquals(popular_proposal.organization.name, self.org.name)
        self.assertEquals(popular_proposal.area, self.arica)
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

        # context = Context({'area': self.arica,
        #                    'temporary_data': temporary_data,
        #                    'moderator': self.feli
        #                    })
        # template_body = get_template('mails/popular_proposal_accepted_body.html')
        # template_subject = get_template('mails/popular_proposal_accepted_subject.html')
        # expected_content= template_body.render(context)
        # expected_subject = template_subject.render(context)
        # self.assertTrue(the_mail.body)
        # self.assertTrue(the_mail.subject)
        # self.assertIn(self.data['title'], str(popular_proposal))
