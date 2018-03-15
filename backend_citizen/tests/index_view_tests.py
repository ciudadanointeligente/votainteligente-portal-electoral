# coding=utf-8
from django.core.urlresolvers import reverse
from backend_citizen.tests import BackendCitizenTestCaseBase, PASSWORD
from backend_candidate.models import Candidacy
from elections.models import Election, Candidate


class IndexViewsTests(BackendCitizenTestCaseBase):
    def setUp(self):
        super(IndexViewsTests, self).setUp()

    def test_index_redirects_if_user(self):
        index_url = reverse('backend_citizen:index')
        update_my_profile_url = reverse('backend_citizen:update_my_profile')
        # Jefe aquí me logeo como la funcionaria más importante
        # de esta fundación
        self.client.login(username=self.fiera.username, password=PASSWORD)
        response = self.client.get(index_url)

        self.assertRedirects(response, update_my_profile_url)

    def test_index_redirect_if_org(self):
        index_url = reverse('backend_citizen:index')
        update_my_profile_url = reverse('organization_profiles:update')

        self.fiera.profile.is_organization = True
        self.fiera.profile.save()

        self.client.login(username=self.fiera.username, password=PASSWORD)

        response = self.client.get(index_url)

        self.assertRedirects(response, update_my_profile_url)

    def test_index_redirect_to_login_if_not_logged_in(self):
        index_url = reverse('backend_citizen:index')
        response = self.client.get(index_url)
        self.assertRedirects(response, reverse('auth_login')+'?next=' + index_url)
    
    def test_index_redirect_if_user_is_not_logged_in(self):
        index_url = reverse('backend_citizen:index')
        election = Election.objects.get(id=2)
        fiera_candidata = Candidate.objects.create(name='Fiera Feroz la mejor candidata del mundo!', slug="fiera")
        Candidacy.objects.create(candidate=fiera_candidata, user=self.fiera)
        election.candidates.add(fiera_candidata)
        update_my_profile_url = reverse('backend_candidate:complete_profile',
                                         kwargs={'slug': election.slug,
                                                 'candidate_slug': fiera_candidata.slug})
        self.client.login(username=self.fiera.username, password=PASSWORD)
        response = self.client.get(index_url)
        self.assertRedirects(response, update_my_profile_url)