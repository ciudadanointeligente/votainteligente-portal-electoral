from elections.models import Candidate
from backend_candidate.models import send_candidate_username_and_password


def send_user_to_candidates():
	for candidate in Candidate.objects.all():
		send_candidate_username_and_password(candidate)