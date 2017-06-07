# coding=utf-8
from django.core.urlresolvers import reverse
from backend_citizen.tests import BackendCitizenTestCaseBase, PASSWORD


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