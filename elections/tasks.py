from celery import task
from elections.models import VotaInteligenteMessage

@task()
def send_mails_using_writeit():
    VotaInteligenteMessage.push_moderated_messages_to_writeit()