# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from elections.models import Election, Candidate
from elections.bin import SecondRoundCreator
from candidator.models import TakenPosition
from django.core.management import call_command
from django.utils.six import StringIO
from preguntales.models import Message, Answer
from constance.test import override_config


class SecondRoundCreationTestCase(TestCase):
    def setUp(self):
        self.tarapaca = Election.objects.get(id=1)
        self.adela = self.tarapaca.candidates.get(id=4)
        self.carlos = self.tarapaca.candidates.get(id=5)

    def test_create_a_second_round(self):
        sc = SecondRoundCreator(self.tarapaca)
        sc.pick_one(self.adela)
        sc.pick_one(self.carlos)
        self.assertEquals(sc.candidates[0], self.adela)
        self.assertEquals(sc.candidates[1], self.carlos)
        sc.set_name('second Round election')

        second_round = sc.get_second_round()

        self.assertIsInstance(second_round, Election)
        self.tarapaca.refresh_from_db()
        self.assertEquals(self.tarapaca.second_round, second_round)

        self.assertEquals(second_round.name, 'second Round election')
        self.assertNotEquals(second_round.slug, self.tarapaca.slug)
        self.assertEquals(second_round.candidates.count(), 2)
        self.assertIn(self.adela, second_round.candidates.all())
        self.assertIn(self.carlos, second_round.candidates.all())

    def test_candidate_get_absolute_url(self):
        sc = SecondRoundCreator(self.tarapaca)
        sc.pick_one(self.adela)
        sc.pick_one(self.carlos)

        second_round = sc.get_second_round()

        self.adela.refresh_from_db()

        self.assertIsNotNone(self.adela.get_absolute_url())

    def test_copy_questions(self):
        sc = SecondRoundCreator(self.tarapaca)
        sc.pick_one(self.adela)
        sc.pick_one(self.carlos)
        second_round = sc.get_second_round()
        self.assertEquals(second_round.categories.count(), self.tarapaca.categories.count())
        for category in self.tarapaca.categories.all():
            _category = second_round.categories.get(name=category.name)
            self.assertEquals(_category.topics.count(), category.topics.count())
            for topic in category.topics.all():
                _topic = _category.topics.get(label=topic.label)
                self.assertTrue(TakenPosition.objects.filter(topic=_topic, person=self.adela))
                self.assertTrue(TakenPosition.objects.filter(topic=_topic, person=self.carlos))
                for position in topic.positions.all():
                    self.assertTrue(_topic.positions.filter(label=position.label))

    def test_copy_messages_and_answers(self):
        candidate3 = Candidate.objects.get(id=6)
        message = Message.objects.create(election=self.tarapaca,
                                         author_name='author',
                                         author_email='author@email.com',
                                         subject='subject',
                                         content='content',
                                         slug='subject-slugified',
                                         accepted=True
                                         )
        message.people.add(self.adela)
        message.people.add(self.carlos)
        message.people.add(candidate3)

        answer = Answer.objects.create(content=u'Hey I\'ve had to speak english in the last couple of days',
                                       message=message,
                                       person=self.adela
                                       )
        sc = SecondRoundCreator(self.tarapaca)
        sc.pick_one(self.adela)
        sc.pick_one(self.carlos)
        second_round = sc.get_second_round()
        the_copied_message = second_round.messages.get()
        self.assertNotEquals(the_copied_message.id, message.id)
        self.assertEquals(the_copied_message.author_name, message.author_name)
        self.assertEquals(the_copied_message.subject, message.subject)
        self.assertEquals(the_copied_message.content, message.content)
        the_copied_answer = the_copied_message.answers.get()
        self.assertNotEquals(the_copied_answer.id, answer.id)
        self.assertEquals(the_copied_answer.content, answer.content)
        self.assertEquals(the_copied_answer.person, self.adela)

    def test_management_command(self):
        out = StringIO()
        previous_count = Election.objects.all().count()
        call_command('cloneelection', self.tarapaca.slug, self.adela.id, self.carlos.id, stdout=out)
        after_count = Election.objects.all().count()
        self.assertEquals(after_count, previous_count + 1)
        second_round = Election.objects.last()
        self.assertEquals(second_round.name, self.tarapaca.name)
        self.assertIn(second_round.name, out.getvalue())
        self.assertIn(second_round.get_absolute_url(), out.getvalue())
