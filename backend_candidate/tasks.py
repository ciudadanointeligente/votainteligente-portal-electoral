from votai_utils.celery import app
from elections.models import Candidate
from backend_candidate.models import send_candidate_a_candidacy_link
from backend_candidate.send_mails_to_candidates import send_user_to_candidates, send_candidate_username_and_password

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


@app.task
def let_candidate_now_about_us():
	for candidate in Candidate.objects.all():
		send_candidate_a_candidacy_link(candidate)


@app.task
def send_candidates_their_username_and_password():
    send_user_to_candidates()

@app.task
def send_candidate_username_and_pasword_task(candidate):
    send_candidate_username_and_password(candidate)
