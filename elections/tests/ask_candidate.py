from elections.tests import VotaInteligenteTestCase as TestCase
from django.core.urlresolvers import reverse
from elections.models import Election


class AskTestCase(TestCase):
	def setUp(self):
		super(AskTestCase, self).setUp()
		self.election = Election.objects.all()[0]

	def test_url_ask(self):
		url = reverse('ask_detail_view', 
			kwargs={
			'slug':self.election.slug
			})
		self.assertTrue(url)

	def test_url_is_reachable_for_ask(self):
		url = reverse('ask_detail_view', 
			kwargs={
			'slug':self.election.slug,
			})
		self.assertTrue(url)
		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)
		self.assertIn('election', response.context)
		self.assertEquals(response.context['election'], self.election)
		self.assertIn('form', response.context)
		self.assertTemplateUsed(response, 'elections/ask_candidate.html')

	def test_submit_message(self):
		url = reverse('ask_detail_view', kwargs={'slug':self.election.slug,})
		response = self.client.post(url, {'people': [self.candidato1.pk, self.candidato2.pk],
											'subject': 'this important issue',
											'content': 'this is a very important message', 
											'author_name': 'my name',
											'author_mail': 'mail@mail.er',
											# 'recaptcha_response_field': 'PASSED'
											}, follow=True
											)



		self.assertTemplateUsed(response, 'elections/ask_candidate.html')
		self.assertEquals(Message.objects.count(), 1)
		self.assertEquals(Message.objects.all()[0].content, 'this is a very important message')
		self.assertEquals(Message.objects.all()[0].subject, 'this important issue')

