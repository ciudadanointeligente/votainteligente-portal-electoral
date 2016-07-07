# coding=utf-8
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from backend_citizen.tests import BackendCitizenTestCaseBase, PASSWORD
from backend_citizen.forms import UserChangeForm


class UpdateMyProfileClass(BackendCitizenTestCaseBase):
    def setUp(self):
        super(UpdateMyProfileClass, self).setUp()

    def test_instanciate_form(self):
        data = {
            'first_name': 'Fiera',
            'last_name': 'Feroz'
        }
        form = UserChangeForm(data=data, instance=self.fiera)
        self.assertTrue(form.is_valid())
        fiera = form.save()
        self.assertEquals(fiera.first_name, data['first_name'])
        self.assertEquals(fiera.last_name, data['last_name'])
