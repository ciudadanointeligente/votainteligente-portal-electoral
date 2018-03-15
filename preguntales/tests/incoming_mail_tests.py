# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from django.test.utils import override_settings
from elections.models import Election, Candidate
from preguntales.models import Message, Answer
from datetime import datetime
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from mock import patch, call
from preguntales.forms import MessageForm
from preguntales.email_parser import EmailAnswer, EmailHandler
from unittest import skip
from preguntales.tests import __testing_mails__, __attachrments_dir__, read_lines
from django.core.files import File
from django.core.management import call_command
import os

THE_CURRENT_MEDIA_ROOT = os.path.dirname(os.path.abspath(__file__)) + '/testing_mails/attachments'

def read_mail(mail):
    return read_lines(__testing_mails__ + mail + '.txt')

def readlines1_mock():
    return read_mail('mail')


def readlines2_mock():
    return read_lines('mail_with_identifier_in_the_content')


def readlines3_mock():
    return read_lines('mail_for_no_message')


def killer_mail():
    return 'this should kill the parser!'


def readlines4_mock():
    return read_lines('mail_from_tony')

class IncomingEmailBase(TestCase):
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
                                              slug=u'subject-slugified',
                                              accepted=True
                                              )
        self.message.people.add(self.candidate1)
        self.message.people.add(self.candidate2)
        self.message.send()
        Answer.objects.all().delete()

class AnswerHandlerTestCase(IncomingEmailBase):
    def setUp(self):
        super(AnswerHandlerTestCase, self).setUp()
        self.photo_fiera = File(open(__attachrments_dir__ +"fiera_parque.jpg", 'rb'))
        self.pdf_file = File(open(__attachrments_dir__ + "hello.pd.pdf", 'rb'))

    def test_class_answer(self):
        email_answer = EmailAnswer()
        self.assertTrue(hasattr(email_answer, 'subject'))
        self.assertTrue(hasattr(email_answer, '_content_text'))
        self.assertTrue(hasattr(email_answer, 'content_html'))
        self.assertTrue(hasattr(email_answer, 'answer_identifier'))
        self.assertTrue(hasattr(email_answer, 'email_from'))
        self.assertTrue(hasattr(email_answer, 'email_to'))
        self.assertTrue(hasattr(email_answer, 'when'))
        self.assertTrue(hasattr(email_answer, 'message_id'))
        email_answer.subject = 'prueba4'
        email_answer.content_text = 'prueba4lafieritaespeluda'
        email_answer.content_html = '<p>prueba4lafieritaespeluda</p>'
        email_answer.answer_identifier = '8974aabsdsfierapulgosa'
        email_answer.email_from = 'falvarez@votainteligente.cl'
        email_answer.email_to = 'Felipe <instance-slug+8974aabsdsfierapulgosa@writeit.org>'
        email_answer.when = 'Wed Jun 26 21:05:33 2013'
        email_answer.message_id = '<CAA5PczfGfdhf29wgK=8t6j7hm8HYsBy8Qg87iTU2pF42Ez3VcQ@mail.gmail.com>'

        self.assertTrue(email_answer)
        self.assertEquals(email_answer.subject, 'prueba4')
        self.assertEquals(email_answer.content_text, 'prueba4lafieritaespeluda')
        self.assertEquals(email_answer.answer_identifier, '8974aabsdsfierapulgosa')
        self.assertEquals(email_answer.email_from, 'falvarez@votainteligente.cl')
        self.assertEquals(email_answer.email_to, 'Felipe <instance-slug+8974aabsdsfierapulgosa@writeit.org>')
        self.assertEquals(email_answer.when, 'Wed Jun 26 21:05:33 2013')
        self.assertEquals(email_answer.message_id, '<CAA5PczfGfdhf29wgK=8t6j7hm8HYsBy8Qg87iTU2pF42Ez3VcQ@mail.gmail.com>')
        self.assertEquals(email_answer.content_html, '<p>prueba4lafieritaespeluda</p>')

    def test_getter_removes_the_identifier(self):
        email_answer = EmailAnswer()
        email_answer.subject = 'prueba4'
        email_answer.answer_identifier = '8974aabsdsfierapulgosa'
        email_answer.content_text = 'prueba4lafieritaespeluda y lo mandé desde este mail devteam+8974aabsdsfierapulgosa@chile.com'
        self.assertFalse(email_answer.answer_identifier in email_answer.content_text)
        self.assertNotIn("devteam+@chile.com", email_answer.content_text)

    def test_it_doesnt_contain_anything_of_the_original_email(self):
        '''If I set the "To" header in the email and use it in the email_answer.recipient
        then I should not be getting her/his email address in the content'''
        email_answer = EmailAnswer()
        email_answer.subject = 'prueba5'
        email_answer.email_to = 'Tony <instance-2+identifier123@writeit.org>'
        email_answer.answer_identifier = 'identifier123'
        email_answer.content_text = (
            u'Thank you for your enquiry. I am completely in favour of this measure,\n'
            u'and will certainly be voting for it.\n'
            u'Tony \n'
            u'<instance-2+identifier123@writeit.org>:')
        # There is an intended extra space after the word 'Tony'
        self.assertNotIn('<instance-', email_answer.content_text)
        self.assertNotIn('> :', email_answer.content_text)
        self.assertNotIn('Tony', email_answer.content_text)

    def test_the_email_answer_can_have_attachments(self):
        '''An email answer can have attachments'''
        email_answer = EmailAnswer()
        email_answer.subject = 'prueba4'
        email_answer.content_text = 'prueba4lafieritaespeluda'
        email_answer.add_attachment(self.photo_fiera)
        email_answer.add_attachment(self.pdf_file)
        self.assertTrue(email_answer.attachments)
        self.assertIn(self.photo_fiera, email_answer.attachments)
        self.assertIn(self.pdf_file, email_answer.attachments)

    def test_email_answer_save(self):
        email_answer = EmailAnswer()
        email_answer.subject = 'prueba4'
        outbound_identifier = self.message.outbound_identifiers.get(person=self.candidate1)
        email_answer.answer_identifier = outbound_identifier.key
        email_answer.content_text = 'Hola Hola esto es una prueba'
        answer = email_answer.save()
        self.assertIsInstance(answer, Answer)
        self.assertEquals(answer.message, self.message)
        self.assertEquals(answer.content, email_answer.content_text)

    @override_settings(MEDIA_ROOT=THE_CURRENT_MEDIA_ROOT)
    def test_save_attachments_on_save(self):
        '''When saving it also calls the save an attachment'''
        email_answer = EmailAnswer()
        outbound_identifier = self.message.outbound_identifiers.get(person=self.candidate1)
        email_answer.answer_identifier = outbound_identifier.key
        email_answer.subject = 'prueba4'
        email_answer.content_text = 'prueba4lafieritaespeluda'
        email_answer.add_attachment(self.photo_fiera)
        email_answer.add_attachment(self.pdf_file)
        answer = email_answer.save()
        self.assertTrue(answer.attachments.filter(name=self.photo_fiera.name))
        self.assertTrue(answer.attachments.filter(name=self.pdf_file.name))


class IncomingTest(IncomingEmailBase):
    def setUp(self):
        super(IncomingTest, self).setUp()
        self.handler = EmailHandler()

    def test_handles_email(self):
        answer_email = self.handler.handle(read_mail('mail'))
        self.assertEquals(answer_email.subject, 'prueba4')
        self.assertIn('prueba4lafieri', answer_email.content_html)
        self.assertEquals(answer_email.answer_identifier, "4aaaabbb")
        self.assertEquals(answer_email.email_from, '=?ISO-8859-1?Q?Felipe_=C1lvarez?= <falvarez@ciudadanointeligente.cl>')
        self.assertEquals(answer_email.when, 'Wed, 26 Jun 2013 17:05:30 -0400')
        self.assertEquals(answer_email.message_id, '<CAA5PczfGfdhf29wgK=8t6j7hm8HYsBy8Qg87iTU2pF42Ez3VcQ@mail.gmail.com>')

    def test_logs_the_incoming_email(self):
        with patch('logging.info') as info:
            info.return_value = None

            answer_email = self.handler.handle(read_mail('mail'))
            expected_log = 'New incoming email from %(from)s sent on %(date)s with subject %(subject)s and content %(content)s'
            expected_log = expected_log % {
                'from': answer_email.email_from,
                'date': answer_email.when,
                'subject': answer_email.subject,
                'content': answer_email.content_text,
                }
            info.assert_called_with(expected_log)

    def test_mail_reading_management_command(self):
        outbound_message = self.message.outbound_identifiers.first()
        outbound_message.key = '4aaaabbb'
        outbound_message.save()

        with patch('sys.stdin') as stdin:
            stdin.attach_mock(readlines1_mock, 'readlines')
            call_command('handleemail')
            self.assertEquals(Answer.objects.count(), 1)
            answer = Answer.objects.first()

            self.assertEquals(answer.message, self.message)
            self.assertEquals(answer.person.person_ptr, outbound_message.person )
            self.assertEquals(answer.content, 'prueba4lafieri')
