# coding=utf-8
from django.contrib.auth.models import User
from backend_citizen.tests import BackendCitizenTestCaseBase, PASSWORD
from organization_profiles.models import OrganizationTemplate, BASIC_FIELDS
from organization_profiles.forms import OrganizationTemplateForm
from django.core.urlresolvers import reverse


class OrganizationTemplateUpdateForm(BackendCitizenTestCaseBase):
    def setUp(self):
        super(OrganizationTemplateUpdateForm, self).setUp()
        self.user = User.objects.create(username='ciudadanoi',
                                        first_name='Ciudadano Inteligente',
                                        password=PASSWORD,
                                        email='mail@mail.com')
        self.user.profile.is_organization = True
        self.user.profile.save()

        self.template = self.user.organization_template

    def test_instanciate_form(self):
        data = {
        }
        for field in BASIC_FIELDS:
            data[field] = None
        data["primary_color"] = "#112233"
        data["secondary_color"] = "#332211"
        form_ = OrganizationTemplateForm(instance=self.template, data=data)
        self.assertTrue(form_.is_valid())
        form_.save()

        template_again = OrganizationTemplate.objects.get(id=self.template.id)
        self.assertEquals(template_again.primary_color, data["primary_color"])
        self.assertEquals(template_again.secondary_color, data["secondary_color"])


class OrganizationTemplateViewTest(BackendCitizenTestCaseBase):
    def setUp(self):
        super(OrganizationTemplateViewTest, self).setUp()
        self.user = User.objects.create(username='ciudadanoi',
                                        first_name='Ciudadano Inteligente',
                                        email='mail@mail.com')
        self.user.set_password(PASSWORD)
        self.user.save()
        self.user.profile.is_organization = True
        self.user.profile.save()

        self.template = self.user.organization_template

    def test_get_url_and_displays_form(self):
        url = reverse('organization_profiles:update')
        self.client.login(username=self.user.username, password=PASSWORD)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertIsInstance(response.context['form'], OrganizationTemplateForm)

    def test_non_organization_user_returns_404(self):
        url = reverse('organization_profiles:update')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)
        #  Si no estás loggeado te redirije
        fiera = User.objects.create(username='FieraFerozInteligente',
                                    first_name='Fiera',
                                    email='f@mail.com')
        fiera.set_password(PASSWORD)
        fiera.save()
        self.client.login(username=fiera.username, password=PASSWORD)
        response = self.client.get(url)
        # Si estás loggeado pero no eres organización, retornas 404
        self.assertEquals(response.status_code, 404)
