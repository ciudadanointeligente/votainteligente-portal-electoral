# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from popolo.models import Area
from elections.models import Election
from django.core.urlresolvers import reverse


class ElectionsPerAreaTestCase(TestCase):
    def test_an_election_can_have_an_area(self):
        argentina = Area.objects.create(name=u'Argentina')
        election = Election.objects.create(
            name='the name',
            slug='the-slug',
            description='this is a description',
            extra_info_title=u'ver más',
            area=argentina,
            extra_info_content=u'Más Información')

        self.assertIn(election, argentina.elections.all())

    def test_there_is_a_url_with_the_area(self):
        argentina = Area.objects.create(name=u'Argentina')
        url = reverse('area', kwargs={'slug': argentina.id})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'elections/area.html')
