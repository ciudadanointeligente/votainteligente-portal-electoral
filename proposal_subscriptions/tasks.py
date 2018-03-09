from votai_utils.celery import app
from proposal_subscriptions.runner import TaskRunner
from proposal_subscriptions.models import CommitmentNotificationSender
# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


@app.task
def send_new_proposals_to_subscribers():
    logger.info('Sending new proposals to subscribers')
    TaskRunner.send()


@app.task
def send_commitment_notifications():
    logger.info('Enviando los compromisos a los usuarios')
    CommitmentNotificationSender.send_to_users()
