# -*- coding: utf-8 -*-
from tastypie.resources import Resource
from django.conf import settings
from elections.models import VotaInteligenteAnswer, VotaInteligenteMessage
from popit.models import Person

class NewAnswerWebHook(Resource):
    class Meta:
        resource_name = settings.NEW_ANSWER_ENDPOINT

    def obj_create(self,bundle,**kwargs):
        message = VotaInteligenteMessage.objects.get(url=bundle.data['message_id'])
        person = Person.objects.get(popit_url=bundle.data['person_id'])
        answer = VotaInteligenteAnswer.objects.create(
            content =  bundle.data['content'],
            person=person,
            message=message
            )
        return bundle

    def detail_uri_kwargs(self, bundle):
        return {}