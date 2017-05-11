# coding=utf-8
from django.contrib.auth.models import User
from backend_citizen.tests import BackendCitizenTestCaseBase, PASSWORD
from backend_citizen.models import Profile
from django.core.urlresolvers import reverse
from organization_profiles.models import OrganizationTemplate


class OrganizationFrontEndTestCase(BackendCitizenTestCaseBase):
    def setUp(self):
        super(OrganizationFrontEndTestCase, self).setUp()
        self.user = User.objects.create(username='ciudadanoi',
                                    first_name='Ciudadano Inteligente',
                                   password=PASSWORD,
                                   email='mail@mail.com')
        self.user.profile.is_organization = True
        self.user.profile.save()

    def test_properties(self):
        url = reverse('organization_profiles:home', kwargs={'slug': self.user.username})
        ## /organization/ciudadanoi
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_return_basic_data(self):
        self.user.organization_template.content = u'<h1>{{org_name}}</h1>'
        self.user.organization_template.save()

        url = reverse('organization_profiles:home', kwargs={'slug': self.user.username})

        response = self.client.get(url)

        self.assertEquals(response.content, u"<h1>"+ str(self.user) + u"</h1>")


class OrganizationTemplateTestCase(BackendCitizenTestCaseBase):
    def setUp(self):
        super(OrganizationTemplateTestCase, self).setUp()
        self.user = User.objects.create(username='ciudadanoi',
                                        password=PASSWORD,
                                        email='mail@mail.com')

    def test_instanciate_model(self):
        self.user.profile.is_organization = True
        self.user.profile.save() #  Acá se crea un OrganizationTemplate
        # y se crea porque en la linea anterior le dijimos que la wea era organización
        template = OrganizationTemplate.objects.get(organization=self.user)
        self.assertTrue(template.content)
        fiera = User.objects.create(username='fiera_feroz',
                                    password=PASSWORD,
                                    email='fiera@mail.com')
        fiera.profile.is_organization = False
        fiera.profile.save()
        self.assertFalse(OrganizationTemplate.objects.filter(organization=fiera))
