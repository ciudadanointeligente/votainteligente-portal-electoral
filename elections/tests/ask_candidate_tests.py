# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from django.core.urlresolvers import reverse
from elections.models import Election, VotaInteligenteMessage, VotaInteligenteAnswer
from elections.forms import MessageForm
from writeit.models import Message, WriteItApiInstance
from datetime import datetime
from popit.models import Person
from django.contrib.sites.models import Site


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

    def test_it_has_the_list_of_already_created_messages(self):
        message = VotaInteligenteMessage.objects.create(api_instance=self.election.writeitinstance.api_instance
            , author_name='author'
            , author_email='author email'
            , subject = u'subject test_accept_message'
            , content = u'Qué opina usted sobre el test_accept_message'
            , writeitinstance=self.election.writeitinstance
            , slug = 'subject-slugified'
            )


        url = reverse('ask_detail_view', 
            kwargs={
            'slug':self.election.slug,
            })
        response = self.client.get(url)
        self.assertIn('writeitmessages', response.context)
        self.assertEquals(len(response.context['writeitmessages']), 1)
        self.assertEquals(response.context['writeitmessages'][0], message)



    def test_submit_message(self):
        url = reverse('ask_detail_view', kwargs={'slug':self.election.slug,})
        self.candidate1.relation.reachable = True
        self.candidate1.relation.save()
        self.candidate2.relation.reachable = True
        self.candidate2.relation.save()
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

        alejandro_guille = Person.objects.get(name='Alejandro Guillier')
        alejandro_guille.relation.reachable = True
        alejandro_guille.relation.save()


        election_candidates = self.election.popit_api_instance.person_set.filter(relation__reachable=True)

        self.assertQuerysetEqual(election_candidates,[repr(r) for r in message_form.fields['people'].queryset])


class VotaInteligenteMessageTestCase(TestCase):
    def setUp(self):
        super(VotaInteligenteMessageTestCase, self).setUp()
        self.election = Election.objects.all()[0]
        self.candidate1 = self.election.popit_api_instance.person_set.all()[0]
        self.candidate2 = self.election.popit_api_instance.person_set.all()[1]

    def test_can_create_a_message_with_a_modetation(self):
        message = VotaInteligenteMessage.objects.create(api_instance=self.election.writeitinstance.api_instance
            , author_name='author'
            , author_email='author email'
            , subject = 'subject'
            , content = 'content'
            , writeitinstance=self.election.writeitinstance
            , slug = 'subject-slugified'
            )
        #It is a writeit message
        self.assertIsInstance(message, Message)
        #I want to make sure it is not moderated
        self.assertFalse(message.moderated)
        self.assertTrue(message.created)
        self.assertIsInstance(message.created,datetime)


    def test_unicode(self):
        message = VotaInteligenteMessage.objects.create(api_instance=self.election.writeitinstance.api_instance
            , author_name='author'
            , author_email='author email'
            , subject = 'subject'
            , content = 'content'
            , writeitinstance=self.election.writeitinstance
            , slug = 'subject-slugified'
            )

        expected_unicode = u'author preguntó "subject" en 2a Circunscripcion Antofagasta'
        self.assertEquals(message.__unicode__(), expected_unicode)


    def test_a_message_has_a_message_detail_url(self):
        message = VotaInteligenteMessage.objects.create(api_instance=self.election.writeitinstance.api_instance
            , author_name='author'
            , author_email='author email'
            , subject = 'subject'
            , content = 'content'
            , writeitinstance=self.election.writeitinstance
            , slug = 'subject-slugified'
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
        message = VotaInteligenteMessage.objects.create(api_instance=self.election.writeitinstance.api_instance
            , author_name='author'
            , author_email='author email'
            , subject = u'subject test_accept_message'
            , content = u'Qué opina usted sobre el test_accept_message'
            , writeitinstance=self.election.writeitinstance
            , slug = 'subject-slugified'
            )
        message.people.add(self.candidate1)
        message.people.add(self.candidate2)

        # just making sure this hasn't changed 
        # 
        

        self.assertFalse(message.remote_id)
        self.assertFalse(message.url)

        # Now I moderate this
        # which means push this to the API and then
        # 
        message.accept_moderation()

        self.assertIsNone(message.remote_id)
        self.assertFalse(message.url)
        self.assertTrue(message.moderated)


    def test_the_class_has_a_function_that_will_push_the_messages_to_the_api(self):
        message1 = VotaInteligenteMessage.objects.create(api_instance=self.election.writeitinstance.api_instance
            , author_name='author'
            , author_email='author email'
            , subject = u'subject test_accept_message'
            , content = u'Qué opina usted sobre el test_accept_message'
            , writeitinstance=self.election.writeitinstance
            , slug = 'subject-slugified'
            , moderated = True
            )
        message1.people.add(self.candidate1)
        message1.people.add(self.candidate2)


        message2 = VotaInteligenteMessage.objects.create(api_instance=self.election.writeitinstance.api_instance
            , author_name='author'
            , author_email='author email'
            , subject = u'subject test_accept_message'
            , content = u'Qué opina usted sobre el test_accept_message'
            , writeitinstance=self.election.writeitinstance
            , slug = 'subject-slugified'
            )
        message2.people.add(self.candidate1)
        message2.people.add(self.candidate2)


        VotaInteligenteMessage.push_moderated_messages_to_writeit()

        message1 = VotaInteligenteMessage.objects.get(id=message1.id)
        message2 = VotaInteligenteMessage.objects.get(id=message2.id)

        self.assertTrue(message1.url)
        self.assertTrue(message1.remote_id)

        self.assertFalse(message2.url)
        self.assertFalse(message2.remote_id)






    def test_reject_message(self):
        message = VotaInteligenteMessage.objects.create(api_instance=self.election.writeitinstance.api_instance
            , author_name='author'
            , author_email='author email'
            , subject = u'subject test_accept_message'
            , content = u'Qué opina usted sobre el test_accept_message'
            , writeitinstance=self.election.writeitinstance
            , slug = 'subject-slugified'
            )
        message.people.add(self.candidate1)
        message.people.add(self.candidate2)

        message.reject_moderation()
        #the message has been moderated
        self.assertFalse(message.remote_id)
        self.assertFalse(message.url)
        self.assertTrue(message.moderated)

class VotaInteligenteAnswerTestCase(TestCase):
    def setUp(self):
        self.election = Election.objects.all()[0]
        self.candidate1 = self.election.popit_api_instance.person_set.all()[0]
        self.candidate2 = self.election.popit_api_instance.person_set.all()[1]
        self.message = VotaInteligenteMessage.objects.create(api_instance=self.election.writeitinstance.api_instance
            , author_name='author'
            , author_email='author email'
            , subject = u'subject test_accept_message'
            , content = u'Qué opina usted sobre el test_accept_message'
            , writeitinstance=self.election.writeitinstance
            , slug = 'subject-slugified'
            )
        self.message.people.add(self.candidate1)

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
        self.candidate1 = self.election.popit_api_instance.person_set.all()[0]
        self.candidate2 = self.election.popit_api_instance.person_set.all()[1]
        
        self.message1 = VotaInteligenteMessage.objects.create(api_instance=self.election.writeitinstance.api_instance
            , author_name='author'
            , author_email='author email'
            , subject = u'I\'m moderated'
            , content = u'Qué opina usted sobre el test_accept_message'
            , writeitinstance=self.election.writeitinstance
            , slug = 'subject-slugified'
            , moderated = True
            )
        self.message2 = VotaInteligenteMessage.objects.create(api_instance=self.election.writeitinstance.api_instance
            , author_name='author'
            , author_email='author email'
            , subject = u'message 3'
            , content = u'Qué opina usted sobre el test_accept_message'
            , writeitinstance=self.election.writeitinstance
            , slug = 'subject-slugified'
            , moderated = True
            )
        self.message3 = VotaInteligenteMessage.objects.create(api_instance=self.election.writeitinstance.api_instance
            , author_name='author'
            , author_email='author email'
            , subject = u'please don\'t moderate me'
            , content = u'Qué opina usted sobre el test_accept_message'
            , writeitinstance=self.election.writeitinstance
            , slug = 'subject-slugified'
            )
        self.message4 = VotaInteligenteMessage.objects.create(api_instance=self.election.writeitinstance.api_instance
            , author_name='author'
            , author_email='author email'
            , subject = u'message 4'
            , content = u'Que opina usted sobre el test_accept_message'
            , writeitinstance=self.election.writeitinstance
            , slug = 'subject-slugified'
            , moderated = True
            )
        self.message4.people.add(self.candidate1)

        self.answer1 = VotaInteligenteAnswer.objects.create(message=self.message4, 
            person=self.candidate1.relation.person,
            content=u'answerto message4')
        self.message5 = VotaInteligenteMessage.objects.create(api_instance=self.election.writeitinstance.api_instance
            , author_name='author'
            , author_email='author email'
            , subject = u'message 5'
            , content = u'Que opina usted sobre el test_accept_message'
            , writeitinstance=self.election.writeitinstance
            , slug = 'subject-slugified'
            , moderated = True
            )


    def test_message_class_has_a_manager(self):
        messages = VotaInteligenteMessage.objects.all()

        self.assertEquals(messages.count(), 5)
        self.assertEquals(messages[0], self.message4)#because it has answers
        self.assertEquals(messages[1], self.message5)#because it was the last created
        self.assertEquals(messages[2], self.message2)#the third should not appear here because it has not been moderated
        self.assertEquals(messages[3], self.message1)
        self.assertEquals(messages[4], self.message3)#this hasn't been moderated


