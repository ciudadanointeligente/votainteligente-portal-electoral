# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase as TestCase
from django.contrib.auth.models import User
from popular_proposal.models import (ProposalLike,
                                     PopularProposal,
                                     )
import json
from popular_proposal.forms import SubscriptionForm
from django.core.urlresolvers import reverse
from django.template import Template, Context
from django.core import mail


PASSWORD = "s3cr3t"


class OrganizationSupportingSomeOneElsesProposalTestCase(TestCase):
    '''
    Cuando una propuesta tiene el corazón de una organización
    se produce lo que llamamos un apadrinamiento.
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
        like = ProposalLike.objects.create(user=self.organization,
                                           proposal=self.proposal)

        self.assertEquals(len(mail.outbox), 1)
        the_mail = mail.outbox[0]
        self.assertIn(self.organization.email, the_mail.to)
        self.assertIn(self.fiera.email, the_mail.to)
        self.assertEquals(len(the_mail.to), original_amount_of_mails + 1)
