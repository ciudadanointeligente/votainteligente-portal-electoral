from numpy import matrix, ones
from constance import config


class Adapter(object):
    def __init__(self, election, positions):
        self.user_positions = positions
        self.user_questions = []
        for position in self.user_positions:
            if position.topic not in self.user_questions:
                self.user_questions.append(position.topic)
        self.candidates = list(election.candidates.order_by('id'))
        self.topics = []
        self.positions = []
        for category in election.categories.all().order_by('id'):
            for topic in category.topics.all().order_by('id'):
                self.topics.append(topic)
                for position in topic.positions.all().order_by('id'):
                    self.positions.append(position)

    def get_responses_vector(self):
        response = []
        for position in self.user_positions:
            topic = position.topic
            for p in topic.positions.all().order_by('id'):
                if p == position:
                    response.append(1)
                else:
                    response.append(0)
        return response

    def get_positions_from_candidate(self, candidate):
        positions = []
        for question in self.user_questions:
            for position in question.positions.order_by('id'):
                if question.taken_positions.filter(person=candidate, position=position):
                    positions.append(1)
                else:
                    positions.append(0)
        return positions

    def get_responses_matrix(self):
        matrix = []
        for candidate in self.candidates:
            matrix.append(self.get_positions_from_candidate(candidate))
        return matrix


class CommitmentsAdapter(object):
    def __init__(self, election, proposals):
        self.candidates = []
        for candidate in election.candidates.order_by('id'):
            self.candidates.append(candidate)
        self.proposals = proposals
        self.ones = ones((len(self.proposals),1))

    def get_commitments_matrix(self):
        _C = []
        for candidate in self.candidates:
            vector = []
            for p in self.proposals:
                if candidate.commitments.filter(proposal=p, commited=True).exists():
                    vector.append(1)
                else:
                    vector.append(0)
            _C.append(vector)
        return matrix(_C)
