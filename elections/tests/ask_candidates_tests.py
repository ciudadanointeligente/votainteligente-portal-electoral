# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from elections import get_writeit_instance
from django.test.utils import override_settings
from elections.models import Election, Candidate, VotaInteligenteMessage, VotaInteligenteAnswer
from writeit.models import Message
from datetime import datetime
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from mock import patch, call
from elections.preguntales_forms import MessageForm
from elections.writeit_functions import get_api_url_for_person, reverse_person_url


@override_settings(WRITEIT_NAME='votainteligente',
                   INSTANCE_URL="/api/v1/instance/1/",
                   WRITEIT_ENDPOINT='http://writeit.ciudadanointeligente.org',
                   WRITEIT_USERNAME='admin',
                   WRITEIT_KEY='a',

                   )
class WriteItTestCase(TestCase):
    pass


class GloballyCreatedWriteItApi(WriteItTestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_writeit_instance_from_globally_set_variables(self):
        '''There is a function that returns a writeit instance where to push messages'''
        instance = get_writeit_instance()
        self.assertEquals(instance.name, 'votainteligente')
        self.assertEquals(instance.url, "/api/v1/instance/1/")
        self.assertEquals(instance.api_instance.url, 'http://writeit.ciudadanointeligente.org')


class VotaInteligenteMessageTestCase(WriteItTestCase):
    def setUp(self):
        self.instance = get_writeit_instance()
        self.election = Election.objects.get(id=1)
        self.candidate1 = Candidate.objects.get(id=4)
        self.candidate2 = Candidate.objects.get(id=5)
        self.candidate3 = Candidate.objects.get(id=6)

    def test_instanciate_a_message(self):
        message = VotaInteligenteMessage.objects.create(election=self.election,
                                                        author_name='author',
                                                        author_email='author@email.com',
                                                        subject='subject',
                                                        content='content',
                                                        slug='subject-slugified'
                                                        )

        self.assertTrue(message)
        self.assertIsInstance(message, Message)
        self.assertFalse(message.moderated)
        self.assertTrue(message.created)
        self.assertIsInstance(message.created,datetime)

    def test_str(self):
        message = VotaInteligenteMessage.objects.create(election=self.election,
                                                        author_name='author',
                                                        author_email='author@email.com',
                                                        subject='subject',
                                                        content='content',
                                                        slug='subject-slugified'
                                                        )

        expected_unicode = 'author preguntó "subject" en 2a Circunscripcion Antofagasta'
        self.assertEquals(message.__str__(), expected_unicode)

    def test_a_message_has_a_message_detail_url(self):
        message = VotaInteligenteMessage.objects.create(election=self.election,
                                                        author_name='author',
                                                        author_email='author@email.com',
                                                        subject='subject',
                                                        content='content',
                                                        slug='subject-slugified'
                                                        )

        url = reverse('message_detail',kwargs={'election_slug':self.election.slug, 'pk':message.id})
        self.assertTrue(url)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertIn('election', response.context)
        self.assertIn('votainteligentemessage', response.context)
        self.assertEquals(response.context['election'], self.election)
        self.assertEquals(response.context['votainteligentemessage'], message)
        self.assertTemplateUsed(response, 'elections/message_detail.html')
        site = Site.objects.get_current()
        self.assertEquals("http://%s%s"%(site.domain,url), message.get_absolute_url())

    def test_accept_message(self):
        message = VotaInteligenteMessage.objects.create(election=self.election,
                                                        author_name='author',
                                                        author_email='author@email.com',
                                                        subject='subject',
                                                        content='content',
                                                        slug='subject-slugified'
                                                        )
        message.people.add(self.candidate1)
        message.people.add(self.candidate2)


        self.assertFalse(message.remote_id)
        self.assertFalse(message.url)
        self.assertFalse(message.moderated)

        # Now I moderate this
        # which means push this to the API and then
        # 
        message.accept_moderation()

        self.assertIsNone(message.remote_id)
        self.assertFalse(message.url)


        self.assertTrue(message.moderated)

    def test_the_class_has_a_function_that_will_push_the_messages_to_the_api(self):
        message = VotaInteligenteMessage.objects.create(election=self.election,
                                                        author_name='author',
                                                        author_email='author@email.com',
                                                        subject='subject',
                                                        content='content',
                                                        slug='subject-slugified',
                                                        moderated=True
                                                        )
        message.people.add(self.candidate1)
        message.people.add(self.candidate2)

        message2 = VotaInteligenteMessage.objects.create(election=self.election,
                                                        author_name='author',
                                                        author_email='author@email.com',
                                                        subject='subject',
                                                        content='content',
                                                        slug='subject-slugified',
                                                        moderated=True
                                                        )
        message2.people.add(self.candidate1)
        message2.people.add(self.candidate2)

        message3 = VotaInteligenteMessage.objects.create(election=self.election,
                                                        author_name='author',
                                                        author_email='author@email.com',
                                                        subject='subject',
                                                        content='content',
                                                        slug='subject-slugified'
                                                        )
        message3.people.add(self.candidate1)
        message3.people.add(self.candidate2)

        with patch('elections.models.VotaInteligenteMessage.push_to_the_api') as method_mock:
            # instance = method_mock.return_value
            method_mock.return_value = 'Fiera feroz'


            VotaInteligenteMessage.push_moderated_messages_to_writeit()

            method_mock.assert_has_calls([call(), call()])

    def test_reject_message(self):
        message = VotaInteligenteMessage.objects.create(election=self.election,
                                                        author_name='author',
                                                        author_email='author@email.com',
                                                        subject='subject',
                                                        content='content',
                                                        slug='subject-slugified'
                                                        )
        message.people.add(self.candidate1)
        message.people.add(self.candidate2)

        self.assertIsNone(message.moderated)

        message.reject_moderation()
        #the message has been moderated
        self.assertFalse(message.remote_id)
        self.assertFalse(message.url)
        self.assertTrue(message.moderated)


class VotaInteligenteAnswerTestCase(TestCase):
    def setUp(self):
        self.instance = get_writeit_instance()
        self.election = Election.objects.get(id=1)
        self.candidate1 = Candidate.objects.get(id=4)
        self.candidate2 = Candidate.objects.get(id=5)
        self.candidate3 = Candidate.objects.get(id=6)
        self.message = VotaInteligenteMessage.objects.create(election=self.election,
                                                        author_name='author',
                                                        author_email='author@email.com',
                                                        subject='subject',
                                                        content='content',
                                                        slug='subject-slugified',
                                                        moderated=True
                                                        )
        self.message.people.add(self.candidate1)
        self.message.people.add(self.candidate2)

    def test_create_an_answer(self):
        answer = VotaInteligenteAnswer.objects.create(
            content=u'Hey I\'ve had to speak english in the last couple of days',
            message=self.message,
            person=self.candidate1
            )

        self.assertTrue(answer)
        self.assertEquals(answer.content, u'Hey I\'ve had to speak english in the last couple of days')
        self.assertEquals(answer.message, self.message)
        self.assertEquals(answer.person, self.candidate1)
        self.assertIsNotNone(answer.created)
        self.assertIsInstance(answer.created, datetime)

        self.assertIn(answer, self.message.answers.all())
        self.assertIn(answer, self.candidate1.answers.all())


class VotaInteligenteMessagesOrderedList(TestCase):
    def setUp(self):
        super(VotaInteligenteMessagesOrderedList, self).setUp()
        self.election = Election.objects.all()[0]
        self.candidate1 = Candidate.objects.get(id=4)
        self.candidate2 = Candidate.objects.get(id=5)
        self.candidate3 = Candidate.objects.get(id=6)
        
        self.message1 = VotaInteligenteMessage.objects.create(election=self.election, 
                                                              author_name='author', 
                                                              author_email='author email', 
                                                              subject = u'I\'m moderated', 
                                                              content = u'Qué opina usted sobre el test_accept_message', 
                                                              slug = 'subject-slugified', 
                                                              moderated = True
                                                              )
        self.message2 = VotaInteligenteMessage.objects.create(election=self.election, 
                                                              author_name='author', 
                                                              author_email='author email', 
                                                              subject = u'message 3', 
                                                              content = u'Qué opina usted sobre el test_accept_message', 
                                                              slug = 'subject-slugified', 
                                                              moderated = True
                                                              )
        self.message3 = VotaInteligenteMessage.objects.create(election=self.election, 
                                                              author_name='author', 
                                                              author_email='author email', 
                                                              subject = u'please don\'t moderate me', 
                                                              content = u'Qué opina usted sobre el test_accept_message', 
                                                              slug = 'subject-slugified'
                                                              )
        self.message4 = VotaInteligenteMessage.objects.create(election=self.election, 
                                                              author_name='author', 
                                                              author_email='author email', 
                                                              subject = u'message 4', 
                                                              content = u'Que opina usted sobre el test_accept_message', 
                                                              slug = 'subject-slugified', 
                                                              moderated = True
                                                              )
        self.message4.people.add(self.candidate1)

        self.answer1 = VotaInteligenteAnswer.objects.create(message=self.message4, 
                                                            person=self.candidate1,
                                                            content=u'answerto message4'
                                                            )
        self.message5 = VotaInteligenteMessage.objects.create(election=self.election, 
                                                              author_name='author', 
                                                              author_email='author email', 
                                                              subject = u'message 5', 
                                                              content = u'Que opina usted sobre el test_accept_message', 
                                                              slug = 'subject-slugified', 
                                                              moderated = True
                                                              )


    def test_message_class_has_a_manager(self):
        messages = VotaInteligenteMessage.ordered.all()

        self.assertEquals(messages.count(), 5)
        self.assertEquals(messages[0], self.message4)#because it has answers
        self.assertEquals(messages[1], self.message5)#because it was the last created
        self.assertEquals(messages[2], self.message2)#the third should not appear here because it has not been moderated
        self.assertEquals(messages[3], self.message1)
        self.assertEquals(messages[4], self.message3)#this hasn't been moderated


class PreguntalesWebTestCase(WriteItTestCase):
    def setUp(self):
        self.election = Election.objects.all()[0]
        self.candidate1 = Candidate.objects.get(id=4)
        self.candidate2 = Candidate.objects.get(id=5)
        self.candidate3 = Candidate.objects.get(id=6)

    def tearDown(self):
        pass

    def test_get_the_url(self):
        url = reverse('ask_detail_view', 
            kwargs={
            'slug':self.election.slug
            })
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
        self.candidate1.email = "email@email.com"
        self.candidate1.save()
        self.candidate2.email = "email@email.com"
        self.candidate2.save()
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
        new_message = VotaInteligenteMessage.objects.all()[0]
        self.assertFalse(new_message.remote_id) 
        self.assertFalse(new_message.url)
        self.assertFalse(new_message.moderated)
        self.assertEquals(new_message.content, 'this is a very important message')
        self.assertEquals(new_message.subject, 'this important issue')
        self.assertEquals(new_message.people.all().count(), 2)

    def test_persons_belongs_to_instance_and_is_reachable(self):
        message_form = MessageForm(election=self.election)

        alejandro_guille = Candidate.objects.get(name='Alejandro Guillier')
        alejandro_guille.email = 'eduardo@guillier.cl'
        alejandro_guille.save()


        election_candidates = self.election.candidates.exclude(email__isnull=True).exclude(email="")

        self.assertQuerysetEqual(election_candidates,[repr(r) for r in message_form.fields['people'].queryset])


class AnswerWebhookTestCase(TestCase):

    def setUp(self):
        super(AnswerWebhookTestCase, self).setUp()
        self.election = Election.objects.all()[0]
        self.candidate1 = Candidate.objects.get(id=4)
        self.candidate2 = Candidate.objects.get(id=5)
        self.candidate3 = Candidate.objects.get(id=6)
        # self.message = VotaInteligenteMessage.objects.create(api_instance=self.election.writeitinstance.api_instance
        #     , author_name='author'
        #     , author_email='author@email.com'
        #     , subject = u'subject test_accept_message'
        #     , content = u'Qué opina usted sobre el test_accept_message'
        #     , writeitinstance=self.election.writeitinstance
        #     , slug = 'subject-slugified'
        #     )
        self.message = VotaInteligenteMessage.objects.create(election=self.election, 
                                                             author_name='author', 
                                                             author_email='author email', 
                                                             subject = u'I\'m moderated', 
                                                             content = u'Qué opina usted sobre el test_accept_message', 
                                                             slug = 'subject-slugified', 
                                                             moderated = True
                                                             )
        self.message.people.add(self.candidate1)

        # Ahora emularé la pasada por writeit
        # Al hacer push_to_the_api writeit le devuelve a
        # writeit-django el identificador y su url para acceder a la API

        self.message.url = '/api/v1/message/1/'
        self.message.remote_id = 1
        self.message.save()

    def test_reverse_person_id(self):
        site = Site.objects.get_current()
        site.domain = 'localhost:8000'
        site.save()

        self.assertEquals(reverse_person_url('http://localhost:8000/api/persons/fiera-feroz'), 'fiera-feroz')


    @override_settings(NEW_ANSWER_ENDPOINT = 'new_answer_comming_expected_to_be_a_hash')
    def test_when_i_post_to_a_point_it_creates_an_answer(self):
        # This comes from writeit
        # Webhooks
        # payload = {
        #     'message_id': '/api/v1/message/{0}/'.format(answer.message.id),
        #     'content': answer.content,
        #     'person': answer.person.name,
        #     'person_id': answer.person.popit_url,
        #     }

        data = {
                'content': 'Example Answer', \
                'person': self.candidate1.name, \
                'person_id': get_api_url_for_person(self.candidate1), \
                'message_id': '/api/v1/message/1/'
            }
        response = self.client.post(reverse('new_answer_endpoint') , 
            format='json', 
            data = data
        )

        self.assertEquals(response.status_code, 200)
        self.assertEquals(self.message.answers.count(), 1)
        answer = self.message.answers.all()[0]
        self.assertEquals(answer.content, 'Example Answer')
        self.assertEquals(answer.person, self.candidate1)


    @override_settings(NEW_ANSWER_ENDPOINT = 'new_answer_comming_expected_to_be_a_hash')
    def test_when_I_send_anything_else_it_doesnt_crash(self):
        data = {
                'content': 'Example Answer', \
                'person': self.candidate1.name, \
                'person_id': 'non_existing_id', \
                'message_id': self.message.url
            }

        response = self.client.post(reverse('new_answer_endpoint') , 
            format='json', 
            data = data
        )
        self.assertEquals(response.status_code, 200)