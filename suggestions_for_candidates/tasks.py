# coding=utf-8
from votai_utils.celery import app
from votai_utils.send_mails import send_mails_to_staff

@app.task
def send_suggestions_tasks(incremental_candidate_filter):
    candidates = incremental_candidate_filter.get_candidates()
    send_mails_to_staff({'candidates': candidates,
                         'filter_': incremental_candidate_filter}, 'notify_staff_suggestion_started')
    incremental_candidate_filter.send_mails(sleep=1)
    send_mails_to_staff({'candidates': candidates,
                         'filter_': incremental_candidate_filter}, 'notify_staff_suggestion_ended')
