# coding=utf-8
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from backend_citizen.tests import BackendCitizenTestCaseBase, PASSWORD
from backend_citizen.forms import UserChangeForm
from backend_citizen.models import Profile


class UserProfileClass(BackendCitizenTestCaseBase):
    def setUp(self):
        super(UserProfileClass, self).setUp()

    def test_instanciate_user_profile(self):
        user = User.objects.create(username='user',
                                   password='password',
                                   email='mail@mail.com')
        self.assertTrue(user.profile)

    def test_properties(self):
        user = User.objects.create(username='user',
                                   password='password',
                                   email='mail@mail.com')

        user.profile.delete()
        profile = Profile.objects.create(user=user,
                                         image=self.get_image(),
                                         is_organization=True,
                                         description=u"Soy una buena usuaria"
                                         )
        self.assertEquals(profile.user, user)
        self.assertTrue(profile.image)
        self.assertTrue(profile.is_organization)
        self.assertTrue(profile.description)


