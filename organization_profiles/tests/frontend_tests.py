# coding=utf-8
from django.contrib.auth.models import User
from backend_citizen.tests import BackendCitizenTestCaseBase, PASSWORD
from backend_citizen.models import Profile
from django.core.urlresolvers import reverse
from organization_profiles.models import OrganizationTemplate, ExtraPage


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
        self.user.organization_template.content = u'<h1>{{object}}</h1>'
        self.user.organization_template.save()
        url = reverse('organization_profiles:home', kwargs={'slug': self.user.username})
        response = self.client.get(url)
        self.assertEquals(response.content, u"<h1>" + str(self.user) + u"</h1>")
        ## Y si ahora le cambio el template debería ser distinto o no?????
        self.user.organization_template.content = u'<h2>{{object}}</h2>'
        self.user.organization_template.save()
        response = self.client.get(url)
        self.assertEquals(response.content,
                          u"<h2>" + str(self.user) + u"</h2>",
                          u"Cambiando el template handlebars cambiar la respuesta")
        ## Y si ahora le cambio el template debería ser distinto o no?????
        self.user.organization_template.content = ""
        self.user.organization_template.save()
        response = self.client.get(url)
        self.assertTrue(response.content, "Si está vacio entonces dibuja el contenido de organization_detail_view.hbs")

    def test_display_basic_data(self):
        self.user.organization_template.logo = self.get_image()
        self.user.organization_template.facebook = u'https://www.facebook.com/ciudadanointeligente'
        self.user.organization_template.secondary_color = '#EEEEDD'
        self.user.organization_template.content = u'<ul><li>logo: {{logo}}</li><li>facebook: {{facebook}}</li><li>secondary_color: {{secondary_color}}</li></ul>'
        self.user.organization_template.save()
        url = reverse('organization_profiles:home', kwargs={'slug': self.user.username})
        response = self.client.get(url)

        self.assertIn(self.user.organization_template.logo.url, response.content)
        self.assertIn(self.user.organization_template.facebook, response.content)
        self.assertIn(self.user.organization_template.secondary_color, response.content)


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
        self.assertEquals(template.content, "")
        fiera = User.objects.create(username='fiera_feroz',
                                    password=PASSWORD,
                                    email='fiera@mail.com')
        fiera.profile.is_organization = False
        fiera.profile.save()
        self.assertFalse(OrganizationTemplate.objects.filter(organization=fiera))
        self.assertIn(str(self.user), str(template))

    def test_extra_fields(self):
        self.user.profile.is_organization = True
        self.user.profile.save()
        template = self.user.organization_template
        template.logo = self.get_image()
        template.background_image = self.get_image()
        template.title = u'Título'
        template.sub_title = u'Bajada'
        template.org_url = u'http://ciudadanointeligente.org'
        template.facebook = u'https://www.facebook.com/ciudadanointeligente'
        template.twitter = u'https://twitter.com/ciudadanoi'
        template.instagram = u'https://www.instagram.com/fiera_feroz/'
        template.primary_color = '#FF00FF'
        template.secondary_color = '#1100FF'
        template.rss_url = 'http://blog.ciudadanointeligente.org/feed.xml'
        template.save()
        template = OrganizationTemplate.objects.get(id=self.user.organization_template.id)
        self.assertTrue(template.logo)
        self.assertTrue(template.background_image)
        self.assertTrue(template.title)
        self.assertTrue(template.sub_title)
        self.assertTrue(template.org_url)
        self.assertTrue(template.facebook)
        self.assertTrue(template.twitter)
        self.assertTrue(template.instagram)
        self.assertTrue(template.primary_color)
        self.assertTrue(template.secondary_color)
        self.assertTrue(template.rss_url)


class ExtraPagesPerOrganization(BackendCitizenTestCaseBase):
    def setUp(self):
        super(ExtraPagesPerOrganization, self).setUp()
        self.user = User.objects.create(username='ciudadanoi',
                                        password=PASSWORD,
                                        email='mail@mail.com')
        self.user.profile.is_organization = True
        self.user.profile.save()

    def test_attributes(self):
        extra_page = ExtraPage.objects.create(template=self.user.organization_template,
                                              title=u"Título",
                                              content=u"## Contenido")
        self.assertEquals(extra_page.template, self.user.organization_template)
        self.assertEquals(extra_page.title, u"Título")
        self.assertEquals(extra_page.content, u"## Contenido")
        self.assertTrue(extra_page.slug)
        ## El regalito
        self.assertIn(u"<h2>Contenido</h2>", extra_page.content_markdown)

    def test_extra_pages_in_content(self):
        self.user.organization_template.content = u'{{#each extra_pages}} {{title}} - {{content}} - {{slug}} {{/each}}'
        self.user.organization_template.save()
        extra_page = ExtraPage.objects.create(template=self.user.organization_template,
                                              title=u"Título",
                                              content=u"## Contenido")

        url = reverse('organization_profiles:home', kwargs={'slug': self.user.username})
        response = self.client.get(url) ## Esto es lo que no es unicode
        content = response.content.decode('utf-8')

        self.assertIn(extra_page.title, content)
        self.assertIn(extra_page.slug, content)
        self.assertIn(extra_page.content_markdown, content)
