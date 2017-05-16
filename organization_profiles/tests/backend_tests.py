# coding=utf-8
from django.contrib.auth.models import User
from backend_citizen.tests import BackendCitizenTestCaseBase, PASSWORD
from organization_profiles.models import OrganizationTemplate, BASIC_FIELDS
from organization_profiles.forms import OrganizationTemplateForm


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
        form_ = OrganizationTemplateForm(data=data)
        self.assertTrue(form_.is_valid())
        form_.save()

        template_again = OrganizationTemplate.objects.get(id=self.template.id)
        self.assertEquals(template_again.primary_color, data["primary_color"])
        self.assertEquals(template_again.secondary_color, data["secondary_color"])

