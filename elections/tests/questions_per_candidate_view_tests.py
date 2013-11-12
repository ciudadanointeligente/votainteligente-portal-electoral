# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from elections.models import Election, VotaInteligenteMessage, VotaInteligenteAnswer
from candideitorg.models import Candidate
from django.core.urlresolvers import reverse
from popit.models import Person


class QuestionsPerCandidateViewTestCase(TestCase):
    def setUp(self):
        super(QuestionsPerCandidateViewTestCase, self).setUp()
        self.election = Election.objects.all()[0]
        self.candidate1 = Candidate.objects.get(name="Manuel Rojas").relation.person
        self.candidate2 = Candidate.objects.get(name="Alejandro Guillier").relation.person
        self.candidate3 = Candidate.objects.get(name="Pedro Araya").relation.person
        self.candidate4 = Candidate.objects.get(name="Gisela Contreras").relation.person

        Candidate.objects.exclude(id__in=[self.candidate1.id,
            self.candidate2.id,
            self.candidate3.id,
            self.candidate4.id
            ]).delete()

        Person.objects.exclude(id__in=[self.candidate1.relation.person.id,
            self.candidate2.relation.person.id,
            self.candidate3.relation.person.id,
            self.candidate4.relation.person.id
            ]
            ).delete()


        self.message1 = VotaInteligenteMessage.objects.create(api_instance=self.election.writeitinstance.api_instance
            , author_name='author'
            , author_email='author email'
            , subject = u'subject test_accept_message'
            , content = u'Que opina usted sobre el test_accept_message'
            , writeitinstance=self.election.writeitinstance
            , slug = 'subject-slugified'
            )
        self.message1.people.add(self.candidate1)
        self.message1.people.add(self.candidate2)
        self.message1.people.add(self.candidate3)
        self.message1.people.add(self.candidate4)

        self.answer1_1 = VotaInteligenteAnswer.objects.create(
            content=u'the format is self.answer<number_of_question>_<candidate>',
            message=self.message1,
            person=self.candidate1
            )

        self.message2 = VotaInteligenteMessage.objects.create(api_instance=self.election.writeitinstance.api_instance
            , author_name='author'
            , author_email='author email'
            , subject = u'subject test_accept_message2'
            , content = u'Que opina usted sobre el test_accept_message2'
            , writeitinstance=self.election.writeitinstance
            , slug = 'subject-slugified'
            )
        self.message2.people.add(self.candidate1)
        self.message2.people.add(self.candidate2)
        self.message2.people.add(self.candidate3)
        self.message2.people.add(self.candidate4)
        self.answer2_1 = VotaInteligenteAnswer.objects.create(
            content=u'the format is self.answer2_1',
            message=self.message2,
            person=self.candidate1
            )
        self.answer2_2 = VotaInteligenteAnswer.objects.create(
            content=u'the format is self.answer2_2',
            message=self.message2,
            person=self.candidate2
            )

        
        self.message3 = VotaInteligenteMessage.objects.create(api_instance=self.election.writeitinstance.api_instance
            , author_name='author'
            , author_email='author email'
            , subject = u'subject test_accept_message3'
            , content = u'Que opina usted sobre el test_accept_message3'
            , writeitinstance=self.election.writeitinstance
            , slug = 'subject-slugified'
            )
        self.message3.people.add(self.candidate1)
        self.message3.people.add(self.candidate2)
        self.message3.people.add(self.candidate3)
        self.message3.people.add(self.candidate4)

        self.answer3_1 = VotaInteligenteAnswer.objects.create(
            content=u'the format is self.answer3_1',
            message=self.message3,
            person=self.candidate1
            )
        self.answer3_2 = VotaInteligenteAnswer.objects.create(
            content=u'the format is self.answer3_2',
            message=self.message3,
            person=self.candidate2
            )
        self.answer3_4 = VotaInteligenteAnswer.objects.create(
            content=u'the format is self.answer3_2',
            message=self.message3,
            person=self.candidate4
            )

        self.message4 = VotaInteligenteMessage.objects.create(api_instance=self.election.writeitinstance.api_instance
            , author_name='author'
            , author_email='author email'
            , subject = u'subject test_accept_message4'
            , content = u'Que opina usted sobre el test_accept_message4'
            , writeitinstance=self.election.writeitinstance
            , slug = 'subject-slugified'
            )
        self.message4.people.add(self.candidate1)
        self.message4.people.add(self.candidate2)
        self.message4.people.add(self.candidate3)


    def test_it_is_reachable(self):
        reverse_url = reverse('questions_per_candidate', kwargs={'election_slug':self.election.slug,
            'slug':self.candidate1.relation.candidate.slug})

        response = self.client.get(reverse_url)
        self.assertEquals(response.status_code,200)
        self.assertIn('candidate', response.context)
        self.assertEquals(response.context['candidate'], self.candidate1.relation.candidate)
        self.assertTemplateUsed(response, 'elections/questions_per_candidate.html')
        self.assertIn('questions', response.context)
        self.assertEquals(list(response.context['questions']), list(VotaInteligenteMessage.objects.filter(people=self.candidate1)))

