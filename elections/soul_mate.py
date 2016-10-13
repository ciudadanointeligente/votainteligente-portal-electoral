# coding=utf-8
import re
from candidator.comparer import Comparer, InformationHolder
from candidator.adapters import CandidatorCalculator, CandidatorAdapter
from candidator.models import Position
from elections.models import Election
from django.views.generic import DetailView
from candidator.models import Topic, TakenPosition


class VotaInteligenteAdapter(CandidatorAdapter):
    def is_topic_category_the_same_as(self, topic, category):
        return topic.category == category.category_ptr


class SoulMateDetailView(DetailView):
    model = Election
    adapter_class = VotaInteligenteAdapter
    calculator_class = CandidatorCalculator
    layout = "elections/election_base.html"

    def determine_taken_positions(self, positions_dict):
        positions = []
        for key in positions_dict:
            p = re.compile('^question-id-(?P<id>\d+)$')
            m = p.search(key)
            if m:
                _id = int(m.group('id'))
                position_id = positions_dict["question-%d" % (_id)]
                topic_id = positions_dict[key]
                topic = Topic.objects.get(id=topic_id)
                try:
                    position = Position.objects.get(id=position_id)
                    positions.append(TakenPosition(topic=topic,
                                                   position=position
                                                   )
                                     )
                except Position.DoesNotExist:
                    pass
        return positions

    def get_context_data(self, **kwargs):
        context = super(SoulMateDetailView, self).get_context_data(**kwargs)
        context['layout'] = self.layout
        context['result_url'] = self.request.build_absolute_uri()
        return context

    def get_information_holder(self, data={}):
        holder = InformationHolder(adapter=self.adapter_class)
        for category in self.object.categories.all():
            holder.add_category(category)
        for candidate in self.object.candidates.all():
            holder.add_person(candidate)
        if data:
            taken_positions = self.determine_taken_positions(data)
            for taken_position in taken_positions:
                holder.add_position(taken_position)
        return holder


    def post(self, request, *args, **kwargs):
        self.template_name = "elections/soulmate_response.html"
        election = super(SoulMateDetailView, self)\
            .get_object(self.get_queryset())
        self.object = election
        context = self.get_context_data()
        information_holder = self.get_information_holder(data=request.POST)

        comparer = Comparer(adapter_class=self.adapter_class,
                            calculator_class=self.calculator_class)
        result = comparer.compare(information_holder)

        winner_candidate = result[0]['person']
        context['winner'] = result[0]
        context['winner']['candidate'] = winner_candidate

        others_candidates = []
        for other in result[1:]:
            other_candidate = other['person']
            other["candidate"] = other_candidate
            others_candidates.append(other)

        context['others'] = others_candidates
        return self.render_to_response(context)