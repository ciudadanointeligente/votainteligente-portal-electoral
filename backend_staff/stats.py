from elections.models import Candidate
from backend_candidate.models import CandidacyContact
from popular_proposal.models import PopularProposal, Commitment, ProposalLike
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.models import User
from constance import config
from popular_proposal.forms.form_texts import TOPIC_CHOICES

class CandidateParticipation(object):
    no_contact = 0

    def __init__(self, filter_kwargs={}):
        qs = Candidate.objects.all()
        if filter_kwargs:
            qs = qs.filter(**filter_kwargs)

        self.with_us = qs.exclude(candidacy__user__last_login__isnull=True).count()
        self.got_email = qs.filter(contacts__in=CandidacyContact.objects.filter(used_by_candidate=False)).count()
        self.no_contact = qs.filter(contacts__isnull=True, **filter_kwargs).count()


class Stats(object):
    def __init__(self):
        self.all_candidates_qs = Candidate.objects.exclude(elections__area__slug=config.HIDDEN_AREAS)
        self.candidates_qs = self.all_candidates_qs
        super(Stats, self).__init__()

    def total_candidates(self):
        return Candidate.objects.count()

    def participation(self):
        result = CandidateParticipation()
        return result

    def proposals(self):
        return PopularProposal.objects.exclude(for_all_areas=True).count()

    def local_gatherings(self):
        return PopularProposal.objects.filter(is_local_meeting=True).count()

    def commitments(self):
        return Commitment.objects.count()

    @property
    def organizations(self):
        return User.objects.filter(profile__is_organization=True)

    @property
    def likes(self):
        return ProposalLike.objects.count()

    @property
    def likers(self):
        return User.objects.filter(likes__isnull=False).distinct().count()

    @property
    def per_classification_proposals_count(self):

        count = {

        }
        for topic in TOPIC_CHOICES:
            count[topic[0]] = PopularProposal.objects.filter(clasification=topic[0]).count()
        return count

    def candidates_that_have_commited(self, filter_kwargs={}):
        qs = Candidate.objects.exclude(commitments__isnull=True)
        if filter_kwargs:
            qs = qs.filter(**filter_kwargs)
        return qs.count()

    def proposals_with_commitments(self):
        return PopularProposal.objects.exclude(commitments__isnull=True)

    def candidates_that_have_12_naranja(self):
        return self.candidates_qs.exclude(taken_positions__isnull=True)

    @property
    def likes_by_organizations(self):
        return ProposalLike.objects.filter(user__profile__is_organization=True).count()

    @property
    def organizations_online(self):
        return User.objects.filter(profile__is_organization=True)

    @property
    def proposals_made_by_organizations(self):
        return PopularProposal.objects.filter(proposer__profile__is_organization=True)

    def __getattribute__(self, name):
        if name.startswith('total_candidates_'):
            position = name.replace('total_candidates_', '')

            def total_candidates_per_election_filter():
                return Candidate.objects.filter(elections__position=position).count()
            return total_candidates_per_election_filter
        if name.startswith('participation_'):
            position = name.replace('participation_', '')

            def _participacion():
                return CandidateParticipation(filter_kwargs={'elections__position': position})
            return _participacion
        if name.startswith('candidates_that_have_commited_'):
            position = name.replace('candidates_that_have_commited_', '')

            def _candidates_that_have_commited():
                return self.candidates_that_have_commited(filter_kwargs={'elections__position': position})
            return _candidates_that_have_commited
        if name.startswith('candidates_that_have_12_naranja__'):
            position = name.replace('candidates_that_have_12_naranja__', '')

            self.candidates_qs = self.all_candidates_qs.filter(elections__position=position)
            return self.candidates_that_have_12_naranja
        return super(Stats, self).__getattribute__(name)


class PerAreaStaffStats(object):
    def __init__(self, area):
        self.area = area
        self.all_proposals_qs = PopularProposal.objects.filter(area=self.area)
        self.proposals_qs = self.all_proposals_qs
        self.all_commitments_qs = Commitment.objects.filter(proposal__area=self.area)
        self.commitments_qs = self.all_commitments_qs
        self.all_commiters_qs = Candidate.objects.filter(elections__area=self.area).exclude(commitments__isnull=True)
        self.commiters_qs = self.all_commiters_qs
        self.all_candidates_qs = Candidate.objects.exclude(elections__area__slug=config.HIDDEN_AREAS)
        self.all_candidates_qs = self.all_candidates_qs.filter(elections__area=self.area)
        self.candidates_qs = self.all_candidates_qs
        super(PerAreaStaffStats, self).__init__()

    def total_candidates(self):
        return self.candidates_qs

    def proposals(self):
        return self.proposals_qs

    def commitments(self):
        return self.commitments_qs

    def commiters(self):
        return self.commiters_qs

    def candidates_that_have_12_naranja(self):
        return self.candidates_qs.exclude(taken_positions__isnull=True)

    def __getattribute__(self, name):
        if name.startswith('total_candidates__'):
            position = name.replace('total_candidates__', '')
            self.candidates_qs = self.all_candidates_qs.filter(elections__position=position)
            return self.total_candidates
        if name.startswith('proposals__'):
            field_and_value = name.split('__')
            filter_args = {field_and_value[1]: bool(field_and_value[2])}
            self.proposals_qs = self.all_proposals_qs.filter(**filter_args)
            return self.proposals
        if name.startswith('candidates_that_have_12_naranja__'):
            position = name.replace('candidates_that_have_12_naranja__', '')
            self.candidates_qs = self.all_candidates_qs.filter(elections__position=position)
            return self.candidates_that_have_12_naranja
        return super(PerAreaStaffStats, self).__getattribute__(name)
