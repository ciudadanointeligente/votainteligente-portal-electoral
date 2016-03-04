# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from django.test.utils import override_settings
from django.core import mail
from elections.models import Election, Candidate
from preguntales.models import Message, Answer
from writeit.models import Message as WriteItMessage
from datetime import datetime
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from mock import patch, call
from preguntales.forms import MessageForm
from preguntales.tasks import send_mails
from django.template import Context
from django.template.loader import get_template
from unittest import skip

class WriteItTestCase(TestCase):
    pass


class MessageTestCase(WriteItTestCase):
    def setUp(self):
        self.election = Election.objects.get(id=1)
        self.candidate1 = Candidate.objects.get(id=4)
        self.candidate2 = Candidate.objects.get(id=5)
        self.candidate3 = Candidate.objects.get(id=6)

    def test_instanciate_a_message(self):
        message = Message.objects.create(election=self.election,
                                         author_name='author',
                                         author_email='author@email.com',
                                         subject='Perrito',
                                         content='content',
                                         )

        self.assertIsNone(message.accepted)
        self.assertFalse(message.sent)
        self.assertTrue(message.slug)
        self.assertIn(message.slug, 'perrito')
        self.assertIsInstance(message.created,datetime)
        message2 = Message.objects.create(election=self.election,
                                          author_name='author',
                                          author_email='author@email.com',
                                          subject='Perrito',
                                          content='content',
                                          )
        self.assertNotEquals(message.slug, message2.slug)

    def test_str(self):
        message = Message.objects.create(election=self.election,
                                                        author_name='author',
                                                        author_email='author@email.com',
                                                        subject='subject',
                                                        content='content',
                                                        slug='subject-slugified'
                                                        )

        expected_unicode = 'author preguntó "subject" en 2a Circunscripcion Antofagasta'
        self.assertEquals(message.__str__(), expected_unicode)

    def test_a_message_has_a_message_detail_url(self):
        message = Message.objects.create(election=self.election,
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
        message = Message.objects.create(election=self.election,
                                         author_name='author',
                                         author_email='author@email.com',
                                         subject='subject',
                                         content='content',
                                         )
        message.people.add(self.candidate1)
        message.people.add(self.candidate2)

        self.assertFalse(message.accepted)

        # Now I moderate this
        # which means I send an email with a confirmation email
        #
        message.accept_moderation()

        self.assertFalse(message.sent)
        self.assertTrue(message.accepted)

    def test_send_mail(self):
        message = Message.objects.create(election=self.election,
                                         author_name='author',
                                         author_email='author@email.com',
                                         subject='subject',
                                         content='content',
                                         slug='subject-slugified',
                                         accepted=True
                                         )
        message.people.add(self.candidate1)
        message.people.add(self.candidate2)

        self.assertEquals(len(mail.outbox), 0)
        message.send()
        self.assertEquals(len(mail.outbox), 2)
        the_mail = mail.outbox[0]
        self.assertIn(the_mail.to[0], [self.candidate1.email, self.candidate2.email])
        context = Context({'election': self.election,
                           'candidate': self.candidate1,
                           'message': message
                          })
        template_body = get_template('mails/nueva_pregunta_candidato_body.html')
        expected_content= template_body.render(context)
        self.assertEquals(the_mail.body, expected_content)
        template_subject = get_template('mails/nueva_pregunta_candidato_subject.html')
        expected_subject = template_subject.render(context).replace('\n', '').replace('\r', '')
        self.assertEquals(the_mail.subject, expected_subject)
        message = Message.objects.get(id=message.id)
        self.assertTrue(message.sent)

    def test_the_class_has_a_function_that_will_send_mails(self):
        message = Message.objects.create(election=self.election,
                                         author_name='author',
                                         author_email='author@email.com',
                                         subject='subject',
                                         content='content',
                                         slug='subject-slugified',
                                         accepted=True
                                         )
        message.people.add(self.candidate1)
        message.people.add(self.candidate2)

        message2 = Message.objects.create(election=self.election,
                                          author_name='author',
                                          author_email='author@email.com',
                                          subject='subject',
                                          content='content',
                                          slug='subject-slugified',
                                          accepted=True
                                          )
        message2.people.add(self.candidate1)
        message2.people.add(self.candidate2)

        message3 = Message.objects.create(election=self.election,
                                          author_name='author',
                                          author_email='author@email.com',
                                          subject='subject',
                                          content='content',
                                          slug='subject-slugified'
                                          )
        message3.people.add(self.candidate1)
        message3.people.add(self.candidate2)

        self.assertEquals(len(mail.outbox), 0)
        Message.send_mails()
        sent_mails = Message.objects.filter(sent=True)
        self.assertEquals(len(sent_mails), 2)
        self.assertTrue(Message.objects.get(id=message.id).sent)
        self.assertTrue(Message.objects.get(id=message2.id).sent)
        self.assertEquals(len(mail.outbox), 4)

    def test_reject_message(self):
        message = Message.objects.create(election=self.election,
                                                        author_name='author',
                                                        author_email='author@email.com',
                                                        subject='subject',
                                                        content='content',
                                                        slug='subject-slugified'
                                                        )
        message.people.add(self.candidate1)
        message.people.add(self.candidate2)

        self.assertIsNone(message.accepted)

        message.reject_moderation()
        #the message has been moderated
        self.assertFalse(message.accepted)

class AnswerTestCase(TestCase):
    def setUp(self):
        self.election = Election.objects.get(id=1)
        self.candidate1 = Candidate.objects.get(id=4)
        self.candidate2 = Candidate.objects.get(id=5)
        self.candidate3 = Candidate.objects.get(id=6)
        self.message = Message.objects.create(election=self.election,
                                              author_name='author',
                                              author_email='author@email.com',
                                              subject='subject',
                                              content='content',
                                              slug='subject-slugified',
                                              accepted=True
                                              )
        self.message.people.add(self.candidate1)
        self.message.people.add(self.candidate2)

    def test_create_an_answer(self):
        answer = Answer.objects.create(
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

        self.assertIn(answer, self.message.answers_.all())
        self.assertIn(answer, self.candidate1.answers_.all())


class MessagesOrderedList(TestCase):
    def setUp(self):
        super(MessagesOrderedList, self).setUp()
        self.election = Election.objects.all()[0]
        self.candidate1 = Candidate.objects.get(id=4)
        self.candidate2 = Candidate.objects.get(id=5)
        self.candidate3 = Candidate.objects.get(id=6)

        self.message1 = Message.objects.create(election=self.election,
                                                              author_name='author',
                                                              author_email='author email',
                                                              subject=u'I\'m moderated',
                                                              content=u'Qué opina usted sobre el test_accept_message',
                                                              slug='subject-slugified',
                                                              accepted=True
                                                              )
        self.message2 = Message.objects.create(election=self.election,
                                                              author_name='author',
                                                              author_email='author email',
                                                              subject=u'message 3',
                                                              content=u'Qué opina usted sobre el test_accept_message',
                                                              slug='subject-slugified',
                                                              accepted=True
                                                              )
        self.message3 = Message.objects.create(election=self.election,
                                                              author_name='author',
                                                              author_email='author email',
                                                              subject=u'please don\'t moderate me',
                                                              content=u'Qué opina usted sobre el test_accept_message',
                                                              slug='subject-slugified'
                                                              )
        self.message4 = Message.objects.create(election=self.election,
                                                              author_name='author',
                                                              author_email='author email',
                                                              subject=u'message 4',
                                                              content=u'Que opina usted sobre el test_accept_message',
                                                              slug='subject-slugified',
                                                              accepted=True
                                                              )
        self.message4.people.add(self.candidate1)

        self.answer1 = Answer.objects.create(message=self.message4,
                                             person=self.candidate1,
                                             content=u'answerto message4'
                                             )
        self.message5 = Message.objects.create(election=self.election,
                                               author_name='author',
                                               author_email='author email',
                                               subject=u'message 5',
                                               content=u'Que opina usted sobre el test_accept_message',
                                               slug='subject-slugified',
                                               accepted=True
                                               )


    def test_message_class_has_a_manager(self):
        messages = Message.ordered.all()

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
        new_message = Message.objects.all()[0]
        self.assertFalse(new_message.sent)
        self.assertFalse(new_message.accepted)
        self.assertEquals(new_message.content, 'this is a very important message')
        self.assertEquals(new_message.subject, 'this important issue')
        self.assertEquals(new_message.people.all().count(), 2)

    def test_persons_belongs_to_instance_and_is_reachable(self):
        message_form = MessageForm(election=self.election)

        alejandro_guille = Candidate.objects.get(name='Alejandro Guillier')
        alejandro_guille.email = 'eduardo@guillier.cl'
        alejandro_guille.save()


        election_candidates = self.election.candidates.exclude(email__isnull=True).exclude(email="")

        self.assertQuerysetEqual(election_candidates,
                                 [repr(r) for r in message_form.fields['people'].queryset],
                                 ordered=False)


@skip("Estoy sacando todo lo que tenga que ver con writeit lo que implica que no reciviremos mails")
class AnswerWebhookTestCase(TestCase):
    def setUp(self):
        super(AnswerWebhookTestCase, self).setUp()
        self.election = Election.objects.all()[0]
        self.candidate1 = Candidate.objects.get(id=4)
        self.candidate2 = Candidate.objects.get(id=5)
        self.candidate3 = Candidate.objects.get(id=6)
        self.message = Message.objects.create(election=self.election,
                                              author_name='author',
                                              author_email='author email',
                                              subject=u'I\'m moderated',
                                              content=u'Qué opina usted sobre el test_accept_message',
                                              slug='subject-slugified',
                                              accepted=True
                                              )
        self.message.people.add(self.candidate1)

    def test_reverse_person_id(self):
        from elections.writeit_functions import get_api_url_for_person, reverse_person_url
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

        from elections.writeit_functions import get_api_url_for_person, reverse_person_url
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
        self.assertEquals(self.message.answers_.count(), 1)
        answer = self.message.answers_.all()[0]
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


class MessageSenderTestCase(TestCase):
    '''
    This TestCase is intended to provide testing for the periodically
    push VotaInteligente Messages to WriteIt (writeit.ciudadanointeligente.org).
    '''
    def setUp(self):
        self.election = Election.objects.get(id=1)
        self.candidate1 = Candidate.objects.get(id=4)
        self.candidate2 = Candidate.objects.get(id=5)
        self.candidate3 = Candidate.objects.get(id=6)

    def test_push_moderated_messages(self):
        '''Push moderated messages'''
        message = Message.objects.create(election=self.election,
                                         author_name='author',
                                         author_email='author@email.com',
                                         subject='subject',
                                         content='content',
                                         slug='subject-slugified',
                                         accepted=True
                                         )
        message.people.add(self.candidate1)
        message.people.add(self.candidate2)

        message2 = Message.objects.create(election=self.election,
                                          author_name='author',
                                          author_email='author@email.com',
                                          subject='subject',
                                          content='content',
                                          slug='subject-slugified',
                                          accepted=True
                                          )
        message2.people.add(self.candidate1)
        message2.people.add(self.candidate2)

        message3 = Message.objects.create(election=self.election,
                                                        author_name='author',
                                                        author_email='author@email.com',
                                                        subject='subject',
                                                        content='content',
                                                        slug='subject-slugified'
                                                        )
        message3.people.add(self.candidate1)
        message3.people.add(self.candidate2)
        send_mails.delay()
        self.assertEquals(Message.objects.filter(sent=True).count(), 2)
        self.assertIn(message, Message.objects.filter(sent=True))
        self.assertIn(message2, Message.objects.filter(sent=True))
        self.assertEquals(len(mail.outbox), 4)

