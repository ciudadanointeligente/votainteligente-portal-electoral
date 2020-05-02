from django.db.models import AutoField


def copy_model_instance(obj):
    initial = dict([(f.name, getattr(obj, f.name))
                    for f in obj._meta.fields
                    if not isinstance(f, AutoField) and\
                       not f in obj._meta.parents.values()])
    return obj.__class__(**initial)


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
        second_round = copy_model_instance(self.election)
        second_round.id = None
        if self.second_round_name is not None:
            second_round.name = self.second_round_name
        second_round.save()
        for candidate in self.candidates:
            second_round.candidates.add(candidate)
        self.copy_categories(second_round)
        self.election.second_round = second_round
        self.election.save()
        return second_round

    def copy_categories(self, second_round):
        for category in self.election.categories.all():
            category_copy = copy_model_instance(category)
            category_copy.id = None
            category_copy.save()
            second_round.categories.add(category_copy)
            for topic in category.topics.all():
                _topic = copy_model_instance(topic)
                _topic.id = None
                _topic.category = category_copy
                _topic.save()
                for position in topic.positions.all():
                    _position = copy_model_instance(position)
                    _position.id = None
                    _position.topic = _topic
                    _position.save()
                    for taken_position in position.taken_positions.filter(person__in=self.candidates):
                        _taken_position = copy_model_instance(taken_position)
                        _taken_position.id = None
                        _taken_position.position = _position
                        _taken_position.topic = _topic
                        _taken_position.person = taken_position.person
                        _taken_position.save()

