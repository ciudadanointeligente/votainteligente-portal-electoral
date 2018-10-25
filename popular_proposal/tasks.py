# coding=utf-8
from votai_utils.celery import app
from django.contrib.auth.models import User
from popular_proposal.reporter import PeriodicReporter
from constance import config
from votai_utils.send_mails import send_mails_to_staff


@app.task
def report_sender_task():
    users_with_proposals = User.objects.exclude(proposals__isnull=True)

    if not config.PERIODIC_REPORTS_ENABLED:
        users_with_proposals = users_with_proposals.filter(is_staff=True)

    for u in users_with_proposals:
        r = PeriodicReporter(u)
        r.send_mail()
    ##
    send_mails_to_staff({'number': users_with_proposals}, 'notice_to_staff_of_periodic_reports')
