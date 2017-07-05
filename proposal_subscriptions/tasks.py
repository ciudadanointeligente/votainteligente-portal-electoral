from votainteligente.celery import app
from proposal_subscriptions.runner import TaskRunner
# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


@app.task
def send_new_proposals_to_subscribers():
    logger.info('Sending new proposals to subscribers')
    TaskRunner.send()
