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
