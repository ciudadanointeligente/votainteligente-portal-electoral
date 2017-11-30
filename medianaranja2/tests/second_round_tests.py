# coding=utf-8
from .adapter_tests import MediaNaranjaAdaptersBase
from .forms_tests import MediaNaranjaWizardFormTestsBase
from medianaranja2.proposals_getter import ProposalsGetter, ProposalsGetterByReadingGroup
from elections.models import Area, Election, Candidate, QuestionCategory
from candidator.models import Category, Position, TakenPosition, Topic
from django.contrib.auth.models import User
from popular_proposal.models import (PopularProposal,
                                     Commitment,
                                     ProposalLike,
                                     )
from constance.test import override_config
from medianaranja2.models import ReadingGroup
from django.test import override_settings
from medianaranja2.forms import SetupForm



class MediaNaranjaSecondRoundTestCaseBase(MediaNaranjaAdaptersBase):
    def setUp(self):
        super(MediaNaranjaSecondRoundTestCaseBase, self).setUp()
        self.setUpProposals()
        self.setUpQuestions()
        self.election.slug = 'the-election'
        self.election.save()
        self.another_election = Election.objects.create(
            name='another name', slug="another_election", area=self.election.area)
        self.another_category1 = QuestionCategory.objects.create(name="jerarquias", election=self.another_election)
        self.another_topic1 = Topic.objects.create(
            label=u"Deberían existir las jerarquías?",
            category=self.another_category1,
            description=u"This is a description of jerarquías")
        self.another_position1 = Position.objects.create(
            topic=self.another_topic1,
            label=u"No"
        )
        taken_position = TakenPosition.objects.create(topic=self.another_topic1,
                                                      person=self.c1,
                                                      position=self.another_position1)


@override_settings(SECOND_ROUND_ELECTION="the-election")
class MediaNaranjaSecondRoundTestCase(MediaNaranjaSecondRoundTestCaseBase):
    def setUp(self):
        super(MediaNaranjaSecondRoundTestCase, self).setUp()

    
    def test_get_first_form(self):
        data = {
            'categories': [self.category1.id, self.category2.id]
        }
        form = SetupForm(data)
        self.assertTrue(form.is_valid())
        self.assertEquals(form.cleaned_data['element_selector'], self.election)
        data = {
            'categories': [self.another_category1.id]
        }
        form2 = SetupForm(data)
        self.assertFalse(form2.is_valid())
        self.assertNotIn('area', form2.fields)


@override_settings(SECOND_ROUND_ELECTION="the-election")
class MediaNaranjaFormSecondRound(MediaNaranjaWizardFormTestsBase):
    def setUp(self):
        super(MediaNaranjaFormSecondRound, self).setUp()
        self.data_to_be_posted = [
            {'0-categories': [self.category1.id, self.category2.id]
            },
            {'1-' + self.topic1.slug: self.position1.id,
             '1-' + self.topic2.slug: self.position4.id
            },
            {'2-proposals': [self.p1.id, self.p3.id]}
        ]

    def test_wizard_til_the_end(self):
        self.assertTrue(self.complete_wizard())