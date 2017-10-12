# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase
from proposal_subscriptions.models import (CommitmentNotification,
                                           CommitmentNotificationSender,)
from popular_proposal.models import (PopularProposal,
                                     Commitment,
                                     ProposalLike,
                                     )
from elections.models import Candidate
from django.contrib.auth.models import User
from django.core import mail


class CommitmentNotifications(ProposingCycleTestCaseBase):
    def setUp(self):
        super(CommitmentNotifications, self).setUp()
        self.candidate = Candidate.objects.get(id=1)
        self.popular_proposal = PopularProposal.objects.create(proposer=self.fiera,
                                                               data=self.data,
                                                               title=u'This is a title',
                                                               clasification=u'education'
                                                               )
        self.popular_proposal2 = PopularProposal.objects.create(proposer=self.fiera,
                                                               data=self.data,
                                                               title=u'This is a title2',
                                                               clasification=u'education'
                                                               )

    def test_instanciate_a_model(self):
        u = User.objects.create_user(username="user")
        commitment = Commitment.objects.create(candidate=self.candidate,
                                               proposal=self.popular_proposal,
                                               detail=u'Yo me comprometo',
                                               commited=True)
        notification = CommitmentNotification.objects.create(user=u,
                                                             commitment=commitment)
        self.assertTrue(notification.created)
        self.assertFalse(notification.notified)

    def test_create_notifications_on_commitments(self):
        u = User.objects.create_user(username="user")
        ProposalLike.objects.create(user=u,
                                    proposal=self.popular_proposal)
        ProposalLike.objects.create(user=u,
                                    proposal=self.popular_proposal2)
        u2 = User.objects.create_user(username="user2")
        ProposalLike.objects.create(user=u2,
                                    proposal=self.popular_proposal)

        commitment = Commitment.objects.create(candidate=self.candidate,
                                               proposal=self.popular_proposal)

        notifications = CommitmentNotification.objects.all()
        self.assertEquals(notifications.filter(commitment=commitment).count(), 2)
        commitment2 = Commitment.objects.create(candidate=self.candidate,
                                                proposal=self.popular_proposal2)
        notifications = CommitmentNotification.objects.all()
        self.assertEquals(notifications.filter(commitment=commitment2).count(), 1)
        self.assertTrue(notifications.get(user=u2))

    def test_notification_sender_to_users(self):
        u = User.objects.create_user(username="user", email="bono_u1@themail.com")
        ProposalLike.objects.create(user=u,
                                    proposal=self.popular_proposal)
        ProposalLike.objects.create(user=u,
                                    proposal=self.popular_proposal2)
        u2 = User.objects.create_user(username="user2", email="bono_u2@themail.com")
        ProposalLike.objects.create(user=u2,
                                    proposal=self.popular_proposal)
        commitment = Commitment.objects.create(candidate=self.candidate,
                                               commited=True,
                                               proposal=self.popular_proposal)
        commitment2 = Commitment.objects.create(candidate=self.candidate,
                                                commited=True,
                                                proposal=self.popular_proposal2)
        sender = CommitmentNotificationSender(user=u)
        context = sender.get_context()
        self.assertIn(commitment,context['commitments'].all())
        self.assertIn(commitment2, context['commitments'].all())
        self.assertEquals(context['user'], u)
        self.assertEquals(sender.template_prefix, "commitments_summary")
        original_amount_of_mails = len(mail.outbox)
        sender.send()
        self.assertEquals(len(mail.outbox), original_amount_of_mails + 1)
        the_mail = mail.outbox[original_amount_of_mails]
        self.assertIn(u.email, the_mail.to)
        # No están llegando la info sobre los compromisos
        self.assertIn(commitment.get_absolute_url(), the_mail.body)
        # ahora me quiero asegurar que no se envían de nuevo
        sender = CommitmentNotificationSender(user=u)
        sender.send()
        self.assertFalse(CommitmentNotification.objects.filter(user=u, notified=False))
        self.assertEquals(len(mail.outbox), original_amount_of_mails + 1)

    def test_email_sender(self):
        u = User.objects.create_user(username="user", email="bono_u1@themail.com")
        User.objects.create_user(username="user3", email="bono_u3@themail.com")
        ProposalLike.objects.create(user=u,
                                    proposal=self.popular_proposal)
        ProposalLike.objects.create(user=u,
                                    proposal=self.popular_proposal2)
        u2 = User.objects.create_user(username="user2", email="bono_u2@themail.com")
        ProposalLike.objects.create(user=u2,
                                    proposal=self.popular_proposal)
        Commitment.objects.create(candidate=self.candidate,
                                  commited=True,
                                  proposal=self.popular_proposal)
        Commitment.objects.create(candidate=self.candidate,
                                  commited=True,
                                  proposal=self.popular_proposal2)
        original_amount_of_mails = len(mail.outbox)
        CommitmentNotificationSender.send_to_users()

        self.assertEquals(len(mail.outbox), original_amount_of_mails + 2)
        the_mail = mail.outbox[original_amount_of_mails]
        self.assertIn(the_mail.to[0], [u.email, u2.email])
        the_mail2 = mail.outbox[original_amount_of_mails + 1]
        self.assertIn(the_mail2.to[0], [u.email, u2.email])

    def test_unsubscribed_user(self):
        u = User.objects.create_user(username="user", email="bono_u1@themail.com")
        u.profile.unsubscribed = True
        u.profile.save()
        User.objects.create_user(username="user3", email="bono_u3@themail.com")
        ProposalLike.objects.create(user=u,
                                    proposal=self.popular_proposal)
        ProposalLike.objects.create(user=u,
                                    proposal=self.popular_proposal2)
        u2 = User.objects.create_user(username="user2", email="bono_u2@themail.com")
        u2.profile.unsubscribed = True
        u2.profile.save()
        ProposalLike.objects.create(user=u2,
                                    proposal=self.popular_proposal)
        Commitment.objects.create(candidate=self.candidate,
                                  commited=True,
                                  proposal=self.popular_proposal)
        Commitment.objects.create(candidate=self.candidate,
                                  commited=True,
                                  proposal=self.popular_proposal2)
        original_amount_of_mails = len(mail.outbox)
        CommitmentNotificationSender.send_to_users()
        #NO HAY MAILS NUEVOS POR QUE LOS DOS ESTÁN DESSUSCRITOS
        self.assertEquals(len(mail.outbox), original_amount_of_mails)