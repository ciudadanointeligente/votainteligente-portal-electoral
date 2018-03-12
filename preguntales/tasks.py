from votai_utils.celery import app
from preguntales.models import Message

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


@app.task
def send_mails():
    logger.info('Sending mails to the candidates')
    Message.send_mails()
