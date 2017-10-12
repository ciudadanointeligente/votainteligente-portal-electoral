# coding=utf-8
from django.contrib.auth.models import User
from backend_citizen.tests import BackendCitizenTestCaseBase, PASSWORD
from backend_citizen.models import Profile


class UserProfileClass(BackendCitizenTestCaseBase):
    def setUp(self):
        super(UserProfileClass, self).setUp()

    def test_instanciate_user_profile(self):
        user = User.objects.create(username='user',
                                   password=PASSWORD,
                                   email='mail@mail.com')
        self.assertTrue(user.profile)

    def test_properties(self):
        user = User.objects.create(username='user',
                                   password=PASSWORD,
                                   email='mail@mail.com')

        user.profile.delete()
        profile = Profile.objects.create(user=user,
                                         image=self.get_image(),
                                         description=u"Soy una buena usuaria"
                                         )
        self.assertEquals(profile.user, user)
        self.assertTrue(profile.image)
        self.assertTrue(profile.description)
        self.assertFalse(profile.first_time_in_backend_citizen)
        self.assertFalse(profile.is_organization)
        self.assertFalse(profile.is_journalist)
        self.assertFalse(profile.unsubscribed)
        self.assertEquals(len(str(profile.unsubscribe_token)), 36)