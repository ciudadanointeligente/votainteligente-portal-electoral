# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase as TestCase
from django.contrib.auth.models import User
from popular_proposal.models import (ProposalLike,
                                     PopularProposal,
                                     )
from django.core import mail


PASSWORD = "s3cr3t"


class OrganizationSupportingSomeOneElsesProposalTestCase(TestCase):
    '''
    Cuando una propuesta tiene el corazón de una organización
    se produce lo que llamamos un apoyo.
    En este momento se envían dos mails con los contactos de las dos organizaciones
    para que se pongan de acuerdo.
    '''
    def setUp(self):
        super(OrganizationSupportingSomeOneElsesProposalTestCase, self).setUp()
        self.proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                       area=self.arica,
                                                       data=self.data,
                                                       title=u'This is a title'
                                                       )
        self.organization = User.objects.create_user(username='organizacionorganizada',
                                                     password=PASSWORD,
                                                     email='organization@oa.org')
        self.organization.profile.is_organization = True
        self.organization.profile.save()

    def test_one_mail_is_sent_when_an_organization_likes_a_proposal(self):
        original_amount_of_mails = len(mail.outbox)
        ProposalLike.objects.create(user=self.organization,
                                    message=u"Hello there we like you a lot",
                                    proposal=self.proposal)

        # Hay dos nuevos mails
        self.assertEquals(len(mail.outbox), original_amount_of_mails + 2)
        to_the_proposer = mail.outbox[original_amount_of_mails]
        # Este mail está dirigido a quien hizo la propuesta
        self.assertIn(self.fiera.email, to_the_proposer.to)
        self.assertEquals(len(to_the_proposer.to), 1)

        # Este mail está dirigido a quien apoyó la propuesta
        to_the_supporter = mail.outbox[original_amount_of_mails + 1]
        self.assertIn(self.organization.email, to_the_supporter.to)
        self.assertEquals(len(to_the_proposer.to), 1)
