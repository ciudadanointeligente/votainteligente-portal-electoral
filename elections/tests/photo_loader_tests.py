# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from elections.models import Election
from django.core.urlresolvers import reverse
from candideitorg.models import Candidate
from django.core.management import call_command


class PhotoLoaderCase(TestCase):
    def setUp(self):
        super(PhotoLoaderCase, self).setUp()

    def test_it_loads_the_photo_for_an_existing_candidate(self):
        call_command('photo_loader', 'elections/tests/fixtures/candidate_photo_url.csv', verbosity=0)

        jano = Candidate.objects.get(name=u"Alejandro Guillier")
        otro = Candidate.objects.get(name=u"Manuel Rojas")

        self.assertEquals(jano.photo, 'http://upload.wikimedia.org/wikipedia/commons/7/76/Alejandro_Guillier.jpg')
        self.assertEquals(otro.photo, 'http://www.2eso.info/sinonimos/wp-content/uploads/2013/02/feo1.jpg')


    def test_if_the_candidate_does_not_exist_it_does_it_for_the_rest(self):
        call_command('photo_loader', 'elections/tests/fixtures/candidate_photo_url.csv', verbosity=0)

        jano = Candidate.objects.get(name=u"Alejandro Guillier")
        otro = Candidate.objects.get(name=u"Manuel Rojas")

        self.assertEquals(jano.photo, 'http://upload.wikimedia.org/wikipedia/commons/7/76/Alejandro_Guillier.jpg')
        self.assertEquals(otro.photo, 'http://www.2eso.info/sinonimos/wp-content/uploads/2013/02/feo1.jpg')

    def test_it_prepends_url_when_provided(self):
        call_command('photo_loader', 'elections/tests/fixtures/candidate_photo.csv', 'some.site/static/', verbosity=0)

        jano = Candidate.objects.get(name=u"Alejandro Guillier")
        otro = Candidate.objects.get(name=u"Manuel Rojas")

        self.assertEquals(jano.photo, 'some.site/static/Alejandro_Guillier.jpg')
        self.assertEquals(otro.photo, 'some.site/static/feo1.jpg')