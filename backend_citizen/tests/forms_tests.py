# coding=utf-8
from backend_citizen.tests import BackendCitizenTestCaseBase
from backend_citizen.forms import (UserChangeForm,
                                   UserCreationForm,
                                   GroupCreationForm)


class UpdateMyProfileClass(BackendCitizenTestCaseBase):
    def setUp(self):
        super(UpdateMyProfileClass, self).setUp()

    def test_instanciate_form(self):
        data = {'first_name': u'Fiera',
                'last_name': 'Feroz',
                'description': u"La más feroz de todas"}
        image = self.get_image()
        files = {'image': image}
        form = UserChangeForm(data=data, files=files, instance=self.fiera)
        self.assertTrue(form.is_valid())
        fiera = form.save()
        self.assertEquals(fiera.first_name, data['first_name'])
        self.assertEquals(fiera.last_name, data['last_name'])
        self.assertEquals(fiera.profile.description, data['description'])
        self.assertTrue(fiera.profile.image)
        form = UserChangeForm(instance=self.fiera)
        self.assertEquals(form.initial['description'], data['description'])
        self.assertTrue(form.initial['image'])

    def test_create_user_form(self):
        data = {'username': 'user',
                'email': 'user@mail.com',
                'password1': 'pass',
                'password2': 'pass',
                }
        form = UserCreationForm(data=data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEquals(user.username, 'user')
        self.assertEquals(user.email, 'user@mail.com')

    def test_create_organization_form(self):
        data = {'username': 'group',
                'name': 'This Is a Great Group',
                'email': 'group@mail.com',
                'password1': 'pass',
                'password2': 'pass',
                }
        form = GroupCreationForm(data=data)
        self.assertTrue(form.is_valid())
        group = form.save()
        self.assertEquals(group.first_name, data['name'])
        self.assertTrue(group.profile.is_organization)
