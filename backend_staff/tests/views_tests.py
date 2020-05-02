# coding=utf-8
from django.core.urlresolvers import reverse
from elections.tests import VotaInteligenteTestCase as TestCase
from django.contrib.auth.models import User
from popular_proposal.models import ProposalTemporaryData, PopularProposal, Commitment, ProposalLike
from popular_proposal.forms import RejectionForm
from elections.models import Area
from elections.models import Election, Candidate
from django.core import mail
from backend_staff.views import Stats
from backend_staff.stats import PerAreaStaffStats
from backend_candidate.models import CandidacyContact, Candidacy
from popular_proposal.forms.form_texts import TOPIC_CHOICES


NON_STAFF_PASSWORD = 'gatito'
STAFF_PASSWORD = 'perrito'


class StaffHomeViewTest(TestCase):
    def setUp(self):
        super(StaffHomeViewTest, self).setUp()
        self.non_staff = User.objects.create_user(username='non_staff',
                                                  email='nonstaff@perrito.com',
                                                  password=NON_STAFF_PASSWORD)
        self.fiera = User.objects.get(username='fiera')
        self.fiera.set_password(STAFF_PASSWORD)
        self.fiera.save()
        self.feli = User.objects.get(username='feli')
        self.arica = Area.objects.get(id=2)
        self.algarrobo = Area.objects.get(id=1)
        self.data = {
            'problem': u'A mi me gusta la contaminación de Santiago y los autos y sus estresantes ruedas',
            'solution': u'Viajar a ver al Feli una vez al mes',
            'when': u'1_year',
            'allies': u'El Feli y el resto de los cabros de la FCI'
        }
        self.election = Election.objects.get(id=1)
        self.election.position = 'alcalde'
        self.election.save()
        self.candidate1 = Candidate.objects.get(id=1)
        self.candidate2 = Candidate.objects.get(id=2)
        self.candidate3 = Candidate.objects.get(id=3)
        self.election2 = Election.objects.get(id=2)
        self.election2.position = 'concejal'
        self.election2.area = self.algarrobo
        self.election2.save()
        self.candidate4 = Candidate.objects.get(id=4)
        self.candidate5 = Candidate.objects.get(id=5)
        self.candidate6 = Candidate.objects.get(id=6)

    def is_reachable_only_by_staff(self, url, url_kwargs=None):
        url = reverse(url, kwargs=url_kwargs)

        # I'm not logged in
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)

        # I'm logged in but I'm not staff
        self.client.login(username=self.non_staff.username,
                          password=NON_STAFF_PASSWORD)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)

        # I'm logged in and I'm staff
        self.client.login(username=self.fiera.username,
                          password=STAFF_PASSWORD)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        return response

    def test_home_view_only_reachable_by_staff_members(self):
        response = self.is_reachable_only_by_staff('backend_staff:index')
        self.assertTemplateUsed(response, 'backend_staff/index.html')

    def test_get_comments_staff_form_for_popular_proposal(self):
        temporary_data = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                              area=self.arica,
                                                              data=self.data)
        response = self.is_reachable_only_by_staff('backend_staff:popular_proposal_comments',
                                                   url_kwargs={'pk': temporary_data.id})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['temporary_data'], temporary_data)
        self.assertTemplateUsed(response, 'backend_staff/popular_proposal_comments.html')

    def test_post_comments_on_popular_proposals(self):
        temporary_data = ProposalTemporaryData.objects.create(proposer=self.fiera,
                                                              area=self.arica,
                                                              data=self.data)
        data = {'problem': u'',
                'when': u'el plazo no está tan weno',
                'solution': u'',
                'allies': u'Los aliados podrían ser mejores'}

        url = reverse('backend_staff:popular_proposal_comments', kwargs={'pk': temporary_data.id})
        self.client.login(username=self.fiera.username,
                          password=STAFF_PASSWORD)
        response = self.client.post(url, data=data, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'backend_staff/index.html')
        self.assertEquals(len(mail.outbox), 1)
        the_mail = mail.outbox[0]
        self.assertIn(self.fiera.email, the_mail.to)
        self.assertEquals(len(the_mail.to), 1)
        self.assertIn(self.fiera.first_name, the_mail.body)

    def test_context(self):
        data = {
            'problem': u'A mi me gusta la contaminación de Santiago y los autos y sus estresantes ruedas',
            'solution': u'Viajar a ver al Feli una vez al mes',
            'when': u'1_year',
            'allies': u'El Feli y el resto de los cabros de la FCI'
        }
        temporary_data = ProposalTemporaryData.objects.create(proposer=self.feli,
                                                              area=self.arica,
                                                              data=data)
        temporary_data2 = ProposalTemporaryData.objects.create(proposer=self.feli,
                                                               area=self.arica,
                                                               data=data)
        temporary_data3 = ProposalTemporaryData.objects.create(proposer=self.feli,
                                                               status=ProposalTemporaryData.Statuses.InTheirSide,
                                                               area=self.arica,
                                                               data=data)

        # Temporary datas are listed in the index so we can moderate them
        # or update them.

        url = reverse('backend_staff:index')
        self.client.login(username=self.fiera.username,
                          password=STAFF_PASSWORD)

        response = self.client.get(url)

        self.assertIn(temporary_data, response.context['proposals'])
        self.assertIn(temporary_data2, response.context['proposals'])
        self.assertIn(temporary_data3, response.context['proposals'])

    def test_get_proposal_moderation_view(self):
        temporary_data = ProposalTemporaryData.objects.create(proposer=self.feli,
                                                              area=self.arica,
                                                              data=self.data)
        url = reverse('backend_staff:moderate_proposal', kwargs={'pk': temporary_data.id})
        # Credentials checking
        self.assertEquals(self.client.post(url).status_code, 302)
        self.client.login(username=self.non_staff.username,
                          password=NON_STAFF_PASSWORD)
        response = self.client.post(url)
        self.assertEquals(response.status_code, 302)
        self.assertTemplateNotUsed('backend_staff/index.html')

        self.client.login(username=self.fiera.username,
                          password=STAFF_PASSWORD)
        # It does have a get method
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'backend_staff/proposal_moderation.html')
        form = response.context['form']
        self.assertIsInstance(form, RejectionForm)
        self.assertEquals(form.temporary_data, temporary_data)
        self.assertEquals(form.moderator, self.fiera)

    def test_accept_popular_proposal(self):
        temporary_data = ProposalTemporaryData.objects.create(proposer=self.feli,
                                                              area=self.arica,
                                                              data=self.data)
        url = reverse('backend_staff:accept_proposal', kwargs={'pk': temporary_data.id})
        # Credentials checking
        self.assertEquals(self.client.post(url).status_code, 302)
        self.client.login(username=self.non_staff.username,
                          password=NON_STAFF_PASSWORD)
        response = self.client.post(url)
        self.assertEquals(response.status_code, 302)
        self.assertTemplateNotUsed('backend_staff/index.html')
        self.client.login(username=self.fiera.username,
                          password=STAFF_PASSWORD)
        # It does not have a get method
        response = self.client.get(url)
        self.assertEquals(response.status_code, 405)

        response = self.client.post(url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('backend_staff/index.html')
        proposal = PopularProposal.objects.get(data=self.data,
                                               proposer=self.feli,
                                               area=self.arica
                                               )
        self.assertTrue(proposal)

    def test_reject_popular_proposal(self):
        temporary_data = ProposalTemporaryData.objects.create(proposer=self.feli,
                                                              area=self.arica,
                                                              data=self.data)
        url = reverse('backend_staff:reject_proposal', kwargs={'pk': temporary_data.id})
        # Credentials checking
        self.assertEquals(self.client.post(url).status_code, 302)
        self.client.login(username=self.non_staff.username,
                          password=NON_STAFF_PASSWORD)
        response = self.client.post(url)
        self.assertEquals(response.status_code, 302)
        self.assertTemplateNotUsed('backend_staff/index.html')
        self.client.login(username=self.fiera.username,
                          password=STAFF_PASSWORD)
        # It does not have a get method
        response = self.client.get(url)
        self.assertEquals(response.status_code, 405)
        data = {'reason': 'es muy mala'}
        response = self.client.post(url, data=data, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'backend_staff/index.html')
        temporary_data = ProposalTemporaryData.objects.get(id=temporary_data.id)
        self.assertEquals(temporary_data.status, ProposalTemporaryData.Statuses.Rejected)
        self.assertEquals(temporary_data.rejected_reason, data['reason'])

    def test_view_all_commitments(self):
        data = {
            'clasification': 'educacion',
            'title': u'Fiera a Santiago',
            'problem': u'A mi me gusta la contaminación de Santiago y los autos\
 y sus estresantes ruedas',
            'solution': u'Viajar a ver al Feli una vez al mes',
            'when': u'1_year',
            'causes': u'La super distancia',
            'terms_and_conditions': True
        }
        popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                          area=self.arica,
                                                          data=self.data,
                                                          title=u'This is a title',
                                                          clasification=u'education'
                                                          )
        commitment = Commitment.objects.create(candidate=self.candidate1,
                                               proposal=popular_proposal,
                                               detail=u'Yo me comprometo',
                                               commited=True)
        url = reverse('backend_staff:all_commitments')

        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)

        # I'm logged in but I'm not journalist
        self.client.login(username=self.non_staff.username,
                          password=NON_STAFF_PASSWORD)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

        # I'm logged in and I'm staff
        self.fiera.profile.is_journalist = True
        self.fiera.profile.save()
        self.client.login(username=self.fiera.username,
                          password=STAFF_PASSWORD)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertIn(commitment, response.context['commitments'])

    def test_stats_get(self):

        self.is_reachable_only_by_staff('backend_staff:stats')

        url = reverse('backend_staff:stats')
        self.client.login(username=self.fiera.username,
                          password=STAFF_PASSWORD)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertIsInstance(response.context['stats'], Stats)
        self.assertTemplateUsed(response, 'backend_staff/stats.html')

    def test_get_list_of_users(self):

        self.is_reachable_only_by_staff('backend_staff:list_of_users')
        user = User.objects.create_user(username='user', password=NON_STAFF_PASSWORD)
        candidato_user = User.objects.create_user(username='candidato_user', password=NON_STAFF_PASSWORD)

        candidacy1 = Candidacy.objects.create(user=candidato_user, candidate=self.candidate1)

        url = reverse('backend_staff:list_of_users')
        self.client.login(username=self.fiera.username,
                          password=STAFF_PASSWORD)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'backend_staff/list_of_users.html')
        self.assertTrue(response.context['users'])
        self.assertIn(user, response.context['users'])
        self.assertNotIn(candidato_user, response.context['users'])

    def tests_get_local_meetings(self):
        stats = Stats()
        PopularProposal.objects.create(proposer=self.fiera,
                                       area=self.arica,
                                       data=self.data,
                                       title=u'This is a title',
                                       clasification=u'education'
                                       )
        PopularProposal.objects.create(proposer=self.fiera,
                                       area=self.arica,
                                       data=self.data,
                                       is_local_meeting=True,
                                       title=u'This is a title',
                                       clasification=u'education'
                                       )
        PopularProposal.objects.create(proposer=self.fiera,
                                       area=self.arica,
                                       data=self.data,
                                       title=u'This is a title',
                                       is_local_meeting=True,
                                       clasification=u'education'
                                       )
        self.assertEquals(stats.local_gatherings(), 2)

    def test_stats_v2_organizations_supporting(self):
        User.objects.all().delete()
        stats = Stats()
        org = User.objects.create_user(username='organizacion', password='password')
        org.profile.is_organization = True
        org.profile.save()
        org2 = User.objects.create_user(username='organizacion2', password='password')
        org2.profile.is_organization = True
        org2.profile.save()
        normal_user = User.objects.create_user(username='normal_user')

        popular_proposal = PopularProposal.objects.create(proposer=normal_user,
                                                          area=self.arica,
                                                          data=self.data,
                                                          title=u'This is a title',
                                                          clasification=u'education'
                                                          )
        ProposalLike.objects.create(user=org, proposal=popular_proposal)
        another_user = User.objects.create_user(username='another_user')
        ProposalLike.objects.create(user=another_user, proposal=popular_proposal)
        self.assertEquals(stats.likes_by_organizations, 1)
        self.assertEquals(stats.organizations_online.count(), 2)

        PopularProposal.objects.create(proposer=org2,
                                       area=self.arica,
                                       data=self.data,
                                       title=u'This is a title',
                                       clasification=u'education'
                                       )
        PopularProposal.objects.create(proposer=org,
                                       area=self.arica,
                                       data=self.data,
                                       title=u'This is a title',
                                       clasification=u'education'
                                       )
        PopularProposal.objects.create(proposer=org,
                                       area=self.arica,
                                       data=self.data,
                                       title=u'This is a title',
                                       clasification=u'education'
                                       )
        self.assertEquals(stats.proposals_made_by_organizations.count(), 3)
        self.assertIn(org, stats.organizations.all())
        self.assertIn(org2, stats.organizations.all())
        self.assertNotIn(normal_user, stats.organizations.all())
        self.assertEquals(stats.likes, ProposalLike.objects.count())
        self.assertEquals(stats.likers, User.objects.filter(likes__isnull=False).count())

    def test_stats_per_classification(self):
        PopularProposal.objects.create(proposer=self.fiera,
                                       area=self.arica,
                                       data=self.data,
                                       title=u'This is a title',
                                       clasification=TOPIC_CHOICES[1][0]
                                       )
        PopularProposal.objects.create(proposer=self.fiera,
                                       area=self.arica,
                                       data=self.data,
                                       title=u'This is a title',
                                       clasification=TOPIC_CHOICES[2][0]
                                       )
        PopularProposal.objects.create(proposer=self.fiera,
                                       area=self.arica,
                                       data=self.data,
                                       title=u'This is a title',
                                       clasification=TOPIC_CHOICES[3][0]
                                       )
        PopularProposal.objects.create(proposer=self.fiera,
                                       area=self.arica,
                                       data=self.data,
                                       title=u'This is a title',
                                       clasification=TOPIC_CHOICES[3][0]
                                       )
        
        stats = Stats()
        count = stats.per_classification_proposals_count
        self.assertEquals(count[TOPIC_CHOICES[1][0]], 1)
        self.assertEquals(count[TOPIC_CHOICES[2][0]], 1)
        self.assertEquals(count[TOPIC_CHOICES[3][0]], 2)

    def test_stats_mixin(self):
        stats = Stats()
        self.assertTrue(Candidate.objects.count())
        self.assertEquals(stats.total_candidates(), Candidate.objects.count())
        self.assertEquals(stats.total_candidates_alcalde(),
                          Election.objects.get(position='alcalde').candidates.count())
        self.assertEquals(stats.total_candidates_concejal(),
                          Election.objects.get(position='concejal').candidates.count())

        candidates_in_alcaldes_ids = []
        for c in Election.objects.get(position='alcalde').candidates.all():
            candidates_in_alcaldes_ids.append(c.id)

        for c in Election.objects.get(position='concejal').candidates.all():
            self.assertNotIn(c.id, candidates_in_alcaldes_ids)

        # Candidate one has connected
        user1 = User.objects.create_user(username='user1', password='password')
        self.client.login(username=user1.username, password='password')

        candidacy1 = Candidacy.objects.create(user=user1, candidate=self.candidate1)
        CandidacyContact.objects.create(candidate=self.candidate1,
                                        used_by_candidate=True,
                                        candidacy=candidacy1)

        # Candidate 2 got an email but hasn't read it
        user2 = User.objects.create_user(username='user2', password='password')

        candidacy2 = Candidacy.objects.create(user=user2, candidate=self.candidate2)
        CandidacyContact.objects.create(candidate=self.candidate2,
                                        used_by_candidate=False,
                                        candidacy=candidacy2
                                        )
        # Candidate 3 we have no contact with her
        user3 = User.objects.create_user(username='user3')

        Candidacy.objects.create(user=user3, candidate=self.candidate3)

        # Candidate four has connected
        user4 = User.objects.create_user(username='user4', password='password')
        self.client.login(username=user4.username, password='password')

        candidacy4 = Candidacy.objects.create(user=user4, candidate=self.candidate4)
        CandidacyContact.objects.create(candidate=self.candidate4,
                                        used_by_candidate=True,
                                        candidacy=candidacy4)

        # Candidate 5 got an email but hasn't read it
        user5 = User.objects.create_user(username='user5')

        candidacy5 = Candidacy.objects.create(user=user5, candidate=self.candidate5)
        CandidacyContact.objects.create(candidate=self.candidate5,
                                        used_by_candidate=False,
                                        candidacy=candidacy5
                                        )
        # Candidate 6 we have no contact with her
        user6 = User.objects.create_user(username='user6')

        Candidacy.objects.create(user=user6, candidate=self.candidate6)

        self.assertEquals(stats.participation().with_us, 2)
        self.assertEquals(stats.participation().got_email, 2)
        self.assertGreater(stats.participation().no_contact, 1)

        self.assertEquals(stats.participation_alcalde().with_us, 1)
        self.assertEquals(stats.participation_alcalde().got_email, 1)
        self.assertEquals(stats.participation_alcalde().no_contact, 1)

        self.assertEquals(stats.participation_concejal().with_us, 1)
        self.assertEquals(stats.participation_concejal().got_email, 1)
        self.assertEquals(stats.participation_concejal().no_contact, 1)

        popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                          area=self.arica,
                                                          data=self.data,
                                                          title=u'This is a title',
                                                          clasification=u'education'
                                                          )
        popular_proposal2 = PopularProposal.objects.create(proposer=self.fiera,
                                                           area=self.arica,
                                                           data=self.data,
                                                           title=u'This is a title',
                                                           clasification=u'education'
                                                           )
        PopularProposal.objects.create(proposer=self.fiera,
                                       area=self.arica,
                                       data=self.data,
                                       title=u'This is a title',
                                       clasification=u'education',
                                       for_all_areas=True
                                       )
        Commitment.objects.create(candidate=self.candidate1,
                                  proposal=popular_proposal,
                                  detail=u'Yo me comprometo',
                                  commited=True)
        Commitment.objects.create(candidate=self.candidate1,
                                  proposal=popular_proposal2,
                                  detail=u'Yo me comprometo',
                                  commited=True)
        self.assertEquals(stats.proposals(), 2)
        self.assertEquals(stats.commitments(), 2)
        self.assertEquals(stats.candidates_that_have_commited(), 1)
        Commitment.objects.create(candidate=self.candidate6,
                                  proposal=popular_proposal2,
                                  detail=u'Yo me comprometo',
                                  commited=True)

        self.assertEquals(stats.candidates_that_have_commited(), 2)
        self.assertEquals(stats.candidates_that_have_commited_alcalde(), 1)
        self.assertEquals(stats.candidates_that_have_commited_concejal(), 1)
        self.assertIn(popular_proposal, stats.proposals_with_commitments().all())
        self.assertIn(popular_proposal2, stats.proposals_with_commitments().all())

        self.candidate6.taken_positions.all().delete()
        self.assertIn(self.candidate1, stats.candidates_that_have_12_naranja().all())
        self.assertIn(self.candidate2, stats.candidates_that_have_12_naranja().all())
        self.assertIn(self.candidate3, stats.candidates_that_have_12_naranja().all())
        self.assertIn(self.candidate4, stats.candidates_that_have_12_naranja().all())
        self.assertIn(self.candidate5, stats.candidates_that_have_12_naranja().all())
        self.assertNotIn(self.candidate6, stats.candidates_that_have_12_naranja().all())

        self.assertEquals(stats.candidates_that_have_12_naranja().count(), 5)
        election = self.candidate1.election
        election.position = 'alcalde'
        election.save()
        self.assertIn(self.candidate1, stats.candidates_that_have_12_naranja__alcalde().all())
        self.assertIn(self.candidate2, stats.candidates_that_have_12_naranja__alcalde().all())
        self.assertIn(self.candidate3, stats.candidates_that_have_12_naranja__alcalde().all())

        self.assertIn(self.candidate4, stats.candidates_that_have_12_naranja__alcalde().all())
        self.assertIn(self.candidate5, stats.candidates_that_have_12_naranja__alcalde().all())

    def test_get_per_area_stats(self):
        self.is_reachable_only_by_staff('backend_staff:per_area_stats')

        url = reverse('backend_staff:per_area_stats')
        self.client.login(username=self.fiera.username,
                          password=STAFF_PASSWORD)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        for area in Area.objects.all():
            self.assertIn(area.id, response.context['stats'].keys())
            stats_per_area = response.context['stats'][area.id]

            self.assertIsInstance(stats_per_area, PerAreaStaffStats)
            self.assertEquals(stats_per_area.area, area)
        self.assertTemplateUsed(response, 'backend_staff/per_area_stats.html')

    def test_stats_per_area(self):
        popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                          area=self.algarrobo,
                                                          data=self.data,
                                                          title=u'This is a title1',
                                                          clasification=u'education'
                                                          )
        popular_proposal2 = PopularProposal.objects.create(proposer=self.fiera,
                                                           area=self.algarrobo,
                                                           data=self.data,
                                                           title=u'This is a title2',
                                                           clasification=u'education'
                                                           )
        popular_proposal3 = PopularProposal.objects.create(proposer=self.fiera,
                                                           area=self.algarrobo,
                                                           data=self.data,
                                                           title=u'This is a title3',
                                                           clasification=u'education',
                                                           for_all_areas=True
                                                           )
        c1 = Commitment.objects.create(candidate=self.candidate1,
                                       proposal=popular_proposal,
                                       detail=u'Yo me comprometo',
                                       commited=True)
        c2 = Commitment.objects.create(candidate=self.candidate1,
                                       proposal=popular_proposal2,
                                       detail=u'Yo me comprometo',
                                       commited=True)
        c3 = Commitment.objects.create(candidate=self.candidate6,
                                       proposal=popular_proposal2,
                                       detail=u'Yo me comprometo',
                                       commited=True)

        stats = PerAreaStaffStats(self.algarrobo)
        self.assertIn(popular_proposal, stats.proposals().all())
        self.assertIn(popular_proposal2, stats.proposals().all())
        self.assertIn(popular_proposal3, stats.proposals().all())

        self.assertIn(popular_proposal, stats.proposals__for_all_areas__().all())
        self.assertIn(popular_proposal2, stats.proposals__for_all_areas__().all())
        self.assertNotIn(popular_proposal3, stats.proposals__for_all_areas__().all())

        self.assertNotIn(popular_proposal, stats.proposals__for_all_areas__True().all())
        self.assertNotIn(popular_proposal2, stats.proposals__for_all_areas__True().all())
        self.assertIn(popular_proposal3, stats.proposals__for_all_areas__True().all())

        self.assertIn(c1, stats.commitments().all())
        self.assertIn(c2, stats.commitments().all())
        self.assertIn(c3, stats.commitments().all())

        self.assertIn(self.candidate1, stats.commiters().all())
        self.assertNotIn(self.candidate2, stats.commiters().all())
        self.assertNotIn(self.candidate3, stats.commiters().all())
        self.assertNotIn(self.candidate4, stats.commiters().all())
        self.assertNotIn(self.candidate5, stats.commiters().all())
        # candidates with 1/2 naranja
        # candidates_that_have_12_naranja__alcalde
        self.candidate5.taken_positions.all().delete()
        self.assertIn(self.candidate1, stats.candidates_that_have_12_naranja__concejal().all())
        self.assertNotIn(self.candidate5, stats.candidates_that_have_12_naranja__concejal().all())

        self.assertIn(self.candidate1, stats.total_candidates__concejal().all())
        self.assertIn(self.candidate2, stats.total_candidates__concejal().all())
        self.assertIn(self.candidate3, stats.total_candidates__concejal().all())
        self.assertIn(self.candidate4, stats.total_candidates__alcalde().all())
        self.assertIn(self.candidate5, stats.total_candidates().all())
