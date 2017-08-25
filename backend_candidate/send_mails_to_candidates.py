from elections.models import Candidate
from backend_candidate.models import send_candidate_username_and_password


def send_user_to_candidates():
    for candidate in Candidate.objects.all():
        send_candidate_username_and_password(candidate)


excluded = []


def send_user_to_candidate_from(area):
    for election in area.elections.all():
        for candidate in election.candidates.all().exclude(id__in=excluded):
            send_candidate_username_and_password(candidate)

