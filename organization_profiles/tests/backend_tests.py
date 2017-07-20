# coding=utf-8
from django.contrib.auth.models import User
from backend_citizen.tests import BackendCitizenTestCaseBase, PASSWORD
from organization_profiles.models import OrganizationTemplate, BASIC_FIELDS, LOGO_SIZE
from organization_profiles.forms import OrganizationTemplateForm
from popular_proposal.models import PopularProposal, ProposalLike
from django.core.urlresolvers import reverse
from django.template import Template, Context
from django.template.loader import get_template

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
        files = {}
        files['logo'] = self.get_image()
        for field in BASIC_FIELDS:
            data[field] = None
        data["primary_color"] = "#112233"
        data["secondary_color"] = "#332211"
        form_ = OrganizationTemplateForm(instance=self.template, data=data, files=files)
        self.assertTrue(form_.is_valid())
        form_.save()

        template_again = OrganizationTemplate.objects.get(id=self.template.id)
        self.assertEquals(template_again.primary_color, data["primary_color"])
        self.assertEquals(template_again.secondary_color, data["secondary_color"])
        self.assertEquals(template_again.organization.profile.image, template_again.logo)
        self.assertEquals(template_again.logo_small.height, LOGO_SIZE)

        self.assertEquals(template_again.logo_small.width, LOGO_SIZE)


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

    def test_post_url_save_information(self):
        data = {
        }
        url = reverse('organization_profiles:update')
        self.client.login(username=self.user.username, password=PASSWORD)
        for field in BASIC_FIELDS:
            data[field] = ""
        data["primary_color"] = "#CCC"
        data["secondary_color"] = "#DDD"
        response = self.client.post(url, data=data, follow=True)

        template_again = OrganizationTemplate.objects.get(id=self.template.id)
        self.assertEquals(template_again.primary_color, data["primary_color"])
        self.assertEquals(template_again.secondary_color, data["secondary_color"])
        self.assertEquals(response.status_code, 200)

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

    def test_get_url_and_displays_form_for_extrapages(self):
        extra_page = self.template.extra_pages.all()[0]
        url = reverse('organization_profiles:update_extrapage', kwargs={'pk': extra_page.id})
        self.client.login(username=self.user.username, password=PASSWORD)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['form'].instance, extra_page)

    def test_get_dont_get_url_if_not_owner(self):
        extra_page = self.template.extra_pages.all()[0]
        url = reverse('organization_profiles:update_extrapage', kwargs={'pk': extra_page.id})
        response = self.client.get(url)
        #  Si no estás loggeado te redirije
        fiera = User.objects.create(username='FieraFerozInteligente',
                                    first_name='Fiera',
                                    email='f@mail.com')
        fiera.set_password(PASSWORD)
        fiera.save()
        self.client.login(username=fiera.username, password=PASSWORD)
        response = self.client.get(url)
        # Si estás loggeado pero no eres la dueña te retorna 404
        self.assertEquals(response.status_code, 404)

    def test_post_to_change_extrapages(self):
        extra_page = self.template.extra_pages.all()[0]
        url = reverse('organization_profiles:update_extrapage', kwargs={'pk': extra_page.id})
        self.client.login(username=self.user.username, password=PASSWORD)
        response = self.client.post(url,
                                    data={'title': 'titulo', 'content': 'contenido'},
                                    follow=True)
        self.assertEquals(response.status_code, 200)


class OrganizationsTemplateTagsTests(BackendCitizenTestCaseBase):
    def setUp(self):
        super(OrganizationsTemplateTagsTests, self).setUp()

        popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                          area=self.arica,
                                                          data=self.data,
                                                          title=u'Esto es un título'
                                                          )




        self.org1 = User.objects.create(username='ciudadanoi',
                                        first_name='Ciudadano Inteligente',
                                        email='mail@mail.com')
        self.org1.profile.is_organization = True
        self.org1.profile.save()
        self.t1 = self.org1.organization_template
        self.t1.logo = self.get_image()
        self.t1.save()

        self.org2 = User.objects.create(username='org2',
                                        first_name='org2',
                                        email='mail2@mail.com')
        self.org2.profile.is_organization = True
        self.org2.profile.save()

        ProposalLike.objects.create(user=self.org2,
                                    proposal=popular_proposal)

        self.org3 = User.objects.create(username='org3',
                                        first_name='org3',
                                        email='mail2@mail.com')
        self.org3.profile.is_organization = True
        self.org3.profile.save()
        self.t3 = self.org3.organization_template
        self.t3.logo = self.get_image()
        self.t3.save()
        PopularProposal.objects.create(proposer=self.org3,
                                       area=self.arica,
                                       data={"name": "FieraFeroz"},
                                       title=u'This is a title',
                                       clasification=u'education'
                                       )
        PopularProposal.objects.create(proposer=self.org3,
                                       area=self.arica,
                                       data={"name": "FieraFeroz"},
                                       title=u'This is a title',
                                       clasification=u'education'
                                       )

    def test_lists_organizations(self):
        qs = OrganizationTemplate.objects.all()
        #Ordenadas por propuestas y <3s
        self.assertEquals(qs.first(), self.t3)
        self.assertEquals(qs[1], self.org2.organization_template)

    def test_exclude_without_logo(self):
        qs = OrganizationTemplate.objects.only_with_logos()
        self.assertNotIn(self.org2.organization_template, qs)
        self.assertIn(self.t1, qs)
        self.assertIn(self.t3, qs)

    def test_template_tag_of_organization_templates_with_logos(self):
        template = Template("{% load votainteligente_extras %}{% organization_logos %}")
        context = Context({"templates": OrganizationTemplate.objects.only_with_logos()})
        actual_rendered_template = template.render(context)
        template_str = get_template('organizations_logos.html')
        expected_template = template_str.render(context)

        self.assertEqual(actual_rendered_template, expected_template)
