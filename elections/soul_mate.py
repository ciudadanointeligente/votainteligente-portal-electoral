# coding=utf-8
import re
from candidator.comparer import Comparer, InformationHolder
from candidator.adapters import CandidatorCalculator, CandidatorAdapter
from candidator.models import Position
from elections.models import Election
from django.views.generic import DetailView
from candidator.models import Topic, TakenPosition
from django.core.cache import cache
from django.conf import settings
from django.shortcuts import render
from constance import config

class VotaInteligenteAdapter(CandidatorAdapter):
    def get_position_from(self, taken_position):
        if taken_position:
            cache_key = u"position_from_taken_position_" + str(taken_position.id)
            position = cache.get(cache_key)
            if position is None:
                position = taken_position.position
                cache.set(cache_key,
                          position,
                          60 * config.SOUL_MATE_INFO_ABOUT_CANDIDATES_MINUTES)
            return position

    def is_topic_category_the_same_as(self, topic, category):
        return topic.category == category.category_ptr

    def get_taken_position_by(self, person, topic):
        cache_key = u"taken_position_" + str(person.id) + '_' + str(topic.id)
        taken_position = cache.get(cache_key)
        if taken_position:
            return taken_position
        try:
            taken_position = TakenPosition.objects.get(person=person,
                                                       topic=topic)
            cache.set(cache_key, taken_position)
            return taken_position
        except TakenPosition.DoesNotExist:
            return None


class SoulMateDetailView(DetailView):
    model = Election
    adapter_class = VotaInteligenteAdapter
    calculator_class = CandidatorCalculator
    layout = "elections/election_base.html"

    def determine_taken_positions(self, positions_dict):
        positions = []
        p = re.compile('^question-id-(?P<id>\d+)$')
        for key in positions_dict:
            m = p.search(key)
            if m:
                _id = int(m.group('id'))
                position_id = positions_dict["question-%d" % (_id)]
                topic_id = positions_dict[key]
                topic = Topic.objects.get(id=topic_id)
                try:
                    position_cache_key = 'position_' + str(position_id)
                    position = cache.get(position_cache_key)
                    if position is None:
                        position = Position.objects.get(id=position_id)
                        cache.set(position_cache_key,
                                  position,
                                  60 * config.SOUL_MATE_INFO_ABOUT_CANDIDATES_MINUTES)
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
        categories = cache.get(str(self.object.id) + '_categories')
        if categories is None:
            categories = self.object.categories.all()
            cache.set(str(self.object.id) + '_categories',
                      categories,
                      60 * config.SOUL_MATE_INFO_ABOUT_CANDIDATES_MINUTES)
        for category in categories:
            holder.add_category(category)
        candidates = cache.get(str(self.object.id) + '_candidates')
        if candidates is None:
            candidates = self.object.candidates.exclude(taken_positions__isnull=True)
            cache.set(str(self.object.id) + '_candidates',
                      candidates,
                      60 * config.SOUL_MATE_INFO_ABOUT_CANDIDATES_MINUTES)
        for candidate in candidates:
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

        stating_index = 0

        if len(result) and (len(result) == 1 or result[0]['percentage'] > result[1]['percentage']):
            stating_index = 1
            winner_candidate = result[0]['person']
            context['winner'] = result[0]
            context['winner']['candidate'] = winner_candidate

        others_candidates = []
        for other in result[stating_index:]:
            other_candidate = other['person']
            other["candidate"] = other_candidate
            others_candidates.append(other)

        context['others'] = others_candidates
        return self.render_to_response(context)
