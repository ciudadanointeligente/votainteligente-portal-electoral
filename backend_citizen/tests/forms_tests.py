# coding=utf-8
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from backend_citizen.tests import BackendCitizenTestCaseBase, PASSWORD
from backend_citizen.forms import UserChangeForm, UserCreationForm


class UpdateMyProfileClass(BackendCitizenTestCaseBase):
    def setUp(self):
        super(UpdateMyProfileClass, self).setUp()

    def test_instanciate_form(self):
        data = {'first_name': u'Fiera',
                'last_name': 'Feroz',
                'description':u"La más feroz de todas"}
        image = self.get_image()
        files = {'image': image}
        form = UserChangeForm(data=data, files=files, instance=self.fiera)
        self.assertTrue(form.is_valid())
        fiera = form.save()
        self.assertEquals(fiera.first_name, data['first_name'])
        self.assertEquals(fiera.last_name, data['last_name'])
        self.assertEquals(fiera.profile.description, data['description'])
        self.assertTrue(fiera.profile.image)

        ## getting initial
        form = UserChangeForm(instance=self.fiera)
        self.assertEquals(form.initial['description'], data['description'])
        self.assertTrue(form.initial['image'])

    def test_create_user_form(self):
        data = {'username': 'user',
                'email': 'user@mail.com',
                'password1': 'pass',
                'password2': 'pass',
                'is_organization': True
                }
        form = UserCreationForm(data=data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertTrue(user.profile.is_organization)
        self.assertEquals(user.username, 'user')
        self.assertEquals(user.email, 'user@mail.com')
