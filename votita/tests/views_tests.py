# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase
from popular_proposal.tests.wizard_tests import WizardDataMixin
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from votita.models import KidsProposal, KidsGathering
from votita.forms.forms import UpdateGatheringForm, TOPIC_CHOICES, AGE_CHOICES
from popular_proposal.models import PopularProposal


USER_PASSWORD = 'secr3t'


class GateheringCreateViewTestCase(ProposingCycleTestCaseBase, WizardDataMixin):
    def setUp(self):
        super(GateheringCreateViewTestCase, self).setUp()
        self.feli = User.objects.get(username='feli')
        self.feli.set_password(USER_PASSWORD)
        self.feli.save()

    def test_get_to_create_a_gathering(self):
        self.client.login(username=self.feli.username, password=USER_PASSWORD)
        url = reverse('votita:create_gathering')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_get_to_create_a_gathering_non_user(self):
        url = reverse('votita:create_gathering')
        response = self.client.get(url)
        login_url = reverse('auth_login') + "?next=" + url
        self.assertRedirects(response, login_url)

    def test_post_to_create_a_gathering(self):
        self.client.login(username=self.feli.username, password=USER_PASSWORD)
        url = reverse('votita:create_gathering')
        data = {'name': u"Título",
                "presidents_features": ["inteligente"],
                "age_range": AGE_CHOICES[1][0],
                'male': 10,
                'female': 10,
                'others': 10,}
        response = self.client.post(url, data=data, follow=True)
        self.assertEquals(response.context['object'].name, data['name'])
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['object'].proposer, self.feli)
        self.assertEquals(response.context['object'].stats_data['male'],
                          data['male'])

    def test_creating_proposal_for_gathering_get_view(self):
        gathering = KidsGathering.objects.create(name=u"Título",
                                                 proposer=self.feli)
        url = reverse('votita:proposal_for_gathering',
                      kwargs={'pk':gathering.id})
        self.client.login(username=self.feli.username, password=USER_PASSWORD)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertIn('formset', response.context)
        formset = response.context['formset']
        self.assertEquals(formset.instance, gathering)
        self.assertEquals(formset.model, KidsProposal)

    def test_creating_proposal_for_gathering_get_view_by_non_owner(self):
        gathering = KidsGathering.objects.create(name=u"Título",
                                                 proposer=self.feli)
        url = reverse('votita:proposal_for_gathering',
                      kwargs={'pk':gathering.id})
        response = self.client.get(url)
        login_url = reverse('auth_login') + "?next=" + url
        self.assertRedirects(response, login_url)
        # The non owner
        non_owner = User.objects.create_user(username="non_owner", password=USER_PASSWORD)
        self.client.login(username=non_owner.username, password=USER_PASSWORD)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_creating_proposal_for_gathering_post_view(self):
        gathering = KidsGathering.objects.create(name=u"Título",
                                                 proposer=self.feli)
        url = reverse('votita:proposal_for_gathering',
                      kwargs={'pk':gathering.id})

        self.client.login(username=self.feli.username, password=USER_PASSWORD)
        data = {'proposals-0-title': "perrito",
                'proposals-0-clasification': TOPIC_CHOICES[1][0],
                "proposals-1-gathering": 1,
                "proposals-TOTAL_FORMS": 1,
                "proposals-INITIAL_FORMS": 0,
                "proposals-MIN_NUM_FORMS": 1,
                "proposals-MAX_NUM_FORMS": 1000
                }
        response = self.client.post(url, data=data)
        update_gathering_url = reverse('votita:update_gathering',
                                       kwargs={'pk':gathering.id})
        self.assertRedirects(response, update_gathering_url)
        proposal = KidsProposal.objects.get(gathering=gathering)
        self.assertEquals(proposal.title, data['proposals-0-title'])
        self.assertEquals(proposal.proposer, self.feli)
        self.assertEquals(proposal.clasification, data['proposals-0-clasification'])

    def test_update_gathering_get(self):
        gathering = KidsGathering.objects.create(name=u"Título",
                                                 proposer=self.feli)
        url = reverse('votita:update_gathering',
                      kwargs={'pk':gathering.id})
        self.client.login(username=self.feli.username, password=USER_PASSWORD)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        form = response.context['form']
        self.assertIsInstance(form, UpdateGatheringForm)
        self.assertEquals(form.instance, gathering)

    def test_update_gathering_get_view_by_non_owner(self):
        gathering = KidsGathering.objects.create(name=u"Título",
                                                 proposer=self.feli)
        url = reverse('votita:update_gathering',
                      kwargs={'pk':gathering.id})
        response = self.client.get(url)
        login_url = reverse('auth_login') + "?next=" + url
        self.assertRedirects(response, login_url)
        # The non owner
        non_owner = User.objects.create_user(username="non_owner", password=USER_PASSWORD)
        self.client.login(username=non_owner.username, password=USER_PASSWORD)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_get_thanks_for_creating_a_proposal(self):
        gathering = KidsGathering.objects.create(name=u"Título",
                                                 proposer=self.feli)
        url = reverse('votita:thanks_for_creating_a_gathering',
                      kwargs={'pk':gathering.id})
        self.client.login(username=self.feli.username, password=USER_PASSWORD)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['gathering'], gathering)

    def test_get_thanks_for_creating_a_proposal_non_owner(self):
        gathering = KidsGathering.objects.create(name=u"Título",
                                                 proposer=self.feli)
        url = reverse('votita:thanks_for_creating_a_gathering',
                      kwargs={'pk':gathering.id})
        response = self.client.get(url)
        login_url = reverse('auth_login') + "?next=" + url
        self.assertRedirects(response, login_url)
        # The non owner
        non_owner = User.objects.create_user(username="non_owner", password=USER_PASSWORD)
        self.client.login(username=non_owner.username, password=USER_PASSWORD)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_update_gathering_post(self):
        gathering = KidsGathering.objects.create(name=u"Título",
                                                 proposer=self.feli)
        url = reverse('votita:update_gathering',
                      kwargs={'pk':gathering.id})
        self.client.login(username=self.feli.username, password=USER_PASSWORD)
        photo = self.get_image()
        data = {
            'image': photo
        }
        response = self.client.post(url, data=data)
        thanks_url = reverse('votita:thanks_for_creating_a_gathering',
                             kwargs={'pk':gathering.id})
        self.assertRedirects(response, thanks_url)
        g = KidsGathering.objects.get(id=gathering.id)
        self.assertTrue(g.image)

class GatheringViewTestCase(ProposingCycleTestCaseBase, WizardDataMixin):
    def setUp(self):
        super(GatheringViewTestCase, self).setUp()
        self.feli = User.objects.get(username='feli')
        self.feli.set_password(USER_PASSWORD)
        self.feli.save()

    def test_show_gathering_info(self):
        gathering = KidsGathering.objects.create(name=u"Título",
                                                 proposer=self.feli)
        url = reverse('votita:ver_encuentro',
                      kwargs={'pk':gathering.id})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['object'], gathering)

    def test_list_gatherings(self):
        gathering1 = KidsGathering.objects.create(name=u"Título",
                                                  proposer=self.feli)
        gathering2 = KidsGathering.objects.create(name=u"Título",
                                                  proposer=self.feli)
        gathering3 = KidsGathering.objects.create(name=u"Título",
                                                  proposer=self.feli)
        url = reverse('votita:list_gatherings')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertIn(gathering1, response.context['gatherings'].all())
        self.assertIn(gathering2, response.context['gatherings'].all())
        self.assertIn(gathering3, response.context['gatherings'].all())

class LandingPage(ProposingCycleTestCaseBase, WizardDataMixin):
    def test_get_home(self):
        proposal1 = KidsProposal.objects.create(proposer=self.fiera,
                                                area=self.arica,
                                                data=self.data,
                                                title=u'This is a title1',
                                                clasification=u'education'
                                                )
        proposal2 = KidsProposal.objects.create(proposer=self.fiera,
                                                area=self.arica,
                                                data=self.data,
                                                title=u'This is a title2',
                                                clasification=u'education',
                                                featured=True,
                                                )
        url = reverse('votita:index')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'votita/index.html')
        self.assertIn(proposal2, response.context['featured_proposals'])
        self.assertNotIn(proposal1, response.context['featured_proposals'])


class KidsProposalViewsTestCase(ProposingCycleTestCaseBase):
    def test_list_proposals(self):
        p1 = PopularProposal.objects.create(proposer=self.fiera,
                                            data=self.data,
                                            title="Title",
                                            clasification=u'education')
        proposal1 = KidsProposal.objects.create(proposer=self.fiera,
                                                area=self.arica,
                                                data=self.data,
                                                title=u'This is a title1',
                                                clasification=u'education'
                                                )
        proposal2 = KidsProposal.objects.create(proposer=self.fiera,
                                                area=self.arica,
                                                data=self.data,
                                                title=u'This is a title2',
                                                clasification=u'education'
                                                )
        url = reverse("votita:list_proposals")
        response = self.client.get(url)
        self.assertIn(proposal1, response.context['proposals'].all())
        self.assertIn(proposal2, response.context['proposals'].all())
        self.assertNotIn(p1, response.context['proposals'].all())

    def test_detail_view(self):
        proposal1 = KidsProposal.objects.create(proposer=self.fiera,
                                                area=self.arica,
                                                data=self.data,
                                                title=u'This is a title1',
                                                clasification=u'education'
                                                )
        url = reverse("votita:proposal_detail", kwargs={'slug': proposal1.slug})
        self.assertEquals(url, proposal1.get_absolute_url())
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(proposal1, response.context['proposal'])
        self.assertTemplateUsed(response, 'votita/detalle_propuesta.html')


from django.test import override_settings


@override_settings(ROOT_URLCONF='votita.stand_alone_urls')
class StandAloneSite(ProposingCycleTestCaseBase):
    def test_get_all_public_urls(self):
        response = self.client.get(reverse('votita:index'))
        self.assertEquals(response.status_code, 200)

        response = self.client.get(reverse('votita:list_gatherings'))
        self.assertEquals(response.status_code, 200)

        gathering = KidsGathering.objects.create(name=u"Título",
                                                 proposer=self.feli)

        url = reverse('votita:ver_encuentro',
                      kwargs={'pk':gathering.id})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_login_page(self):
        url = reverse('votita_auth:login')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'votita/registration/login_citizens.html')
        self.assertEquals(response.status_code, 200)

    def test_views_redirect_to_login(self):
        url = reverse('votita:create_gathering')
        login_url = reverse('votita_auth:login')
        response = self.client.get(url)
        self.assertRedirects(response, login_url + "?next=" + url)
