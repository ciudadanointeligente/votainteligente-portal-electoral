from votainteligente.celery import app
from elections.models import VotaInteligenteMessage

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


@app.task
def send_mails_using_writeit():
    logger.info('Sending mails to writeit')
    VotaInteligenteMessage.push_moderated_messages_to_writeit()
