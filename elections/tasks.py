from votainteligente.celery import app
from elections.models import VotaInteligenteMessage


@app.task
def send_mails_using_writeit():
    VotaInteligenteMessage.push_moderated_messages_to_writeit()
