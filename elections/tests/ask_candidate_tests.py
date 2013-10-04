from elections.tests import VotaInteligenteTestCase as TestCase
from django.core.urlresolvers import reverse
from elections.models import Election
from elections.forms import MessageForm
from writeit.models import Message



class AskTestCase(TestCase):
	def setUp(self):
		super(AskTestCase, self).setUp()
		self.election = Election.objects.all()[0]
		self.candidate1 = self.election.popit_api_instance.person_set.all()[0]
		self.candidate2 = self.election.popit_api_instance.person_set.all()[1]

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
		self.assertIsInstance(response.context['form'],MessageForm)
		self.assertIn('messages', response.context)
		self.assertTemplateUsed(response, 'elections/ask_candidate.html')


	def test_submit_message(self):
		url = reverse('ask_detail_view', kwargs={'slug':self.election.slug,})
		response = self.client.post(url, {'people': [self.candidate1.pk, self.candidate2.pk],
											'subject': 'this important issue',
											'content': 'this is a very important message', 
											'author_name': 'my name',
											'author_email': 'mail@mail.er',
											# 'recaptcha_response_field': 'PASSED'
											}, follow=True
											)



		self.assertTemplateUsed(response, 'elections/ask_candidate.html')
		self.assertEquals(Message.objects.count(), 1)
		new_message = Message.objects.all()[0]
		self.assertTrue(new_message.remote_id and new_message.url) 
		self.assertEquals(new_message.content, 'this is a very important message')
		self.assertEquals(new_message.subject, 'this important issue')
		self.assertEquals(new_message.people.all().count(), 2)

	def test_persons_belongs_to_instance(self):
		message_form = MessageForm(writeitinstance = self.election.writeitinstance)
		election_candidates = self.election.popit_api_instance.person_set.all()
		self.assertQuerysetEqual(election_candidates,[repr(r) for r in message_form.fields['people'].queryset])
