import copy


class SecondRoundCreator(object):
    def __init__(self, election, *args, **kwargs):
        self.election = election
        self.candidates = []
        self.second_round_name = None

    def pick_one(self, candidate):
        self.candidates.append(candidate)

    def set_name(self, name):
        self.second_round_name = name

    def get_second_round(self):
        second_round = copy.copy(self.election)
        second_round.id = None
        if self.second_round_name is not None:
            second_round.name = self.second_round_name
        second_round.save()
        return second_round
