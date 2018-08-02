# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.models import Case, Value, When, PositiveSmallIntegerField, Sum, F
from popular_proposal.models import PopularProposal, Commitment
from elections.models import Candidate as OriginalCandidate
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from backend_candidate.models import CandidacyContact
from votai_utils.send_mails import send_mail
from django.utils import timezone
import datetime



class MeRepresentaPopularProposal(PopularProposal):
    class Meta:
        proxy = True


class MeRepresentaCommitment(Commitment):
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        return self._save(*args, **kwargs)


NON_MALE_KEY = "F"
NON_WHITE_KEY = {"possible_values": ["PARDA", "PARDA"]}


class ForVolunteersManager(models.Manager):
    def get_queryset(self):
        qs = super(ForVolunteersManager, self).get_queryset()
        qs = qs.annotate(
                        is_women=Case(When(gender='F', then=Value(1)),
                        default=Value(0),
                        output_field=PositiveSmallIntegerField())
                    )
        qs = qs.annotate(is_non_white=Case(When(race__in=NON_WHITE_KEY['possible_values'], then=Value(1)),
                        default=Value(0),
                        output_field=PositiveSmallIntegerField())

                )
        qs = qs.annotate(desprivilegio=F('is_women') + F('is_non_white'))
        return qs

class LimitCandidatesForVolunteers(ForVolunteersManager):
    def get_queryset(self):
        qs = super(LimitCandidatesForVolunteers, self).get_queryset()
        qs = qs.exclude(contacts__isnull=False)
        qs = qs.exclude(is_ghost=True)
        qs = qs.exclude(facebook_contacted=True)
        minutes = 30
        from_time = timezone.now() - datetime.timedelta(minutes=minutes)
        qs = qs.exclude(volunteerincandidate__created__gte=from_time)
        return qs


class Candidate(OriginalCandidate):
    cpf = models.CharField(max_length=1024, unique=True)
    nome_completo = models.CharField(max_length=1024, null=True)
    numero = models.CharField(max_length=1024, null=True)
    race = models.CharField(max_length=1024, null=True)
    original_email = models.EmailField(max_length=1024, null=True)
    email_repeated = models.NullBooleanField()
    is_ghost = models.BooleanField(default=False)
    facebook_contacted = models.BooleanField(default=False)
    data_de_nascimento = models.DateField(null=True)

    partido = models.ForeignKey("Partido", null=True)

    objects = ForVolunteersManager()

    for_volunteers = LimitCandidatesForVolunteers()

class VolunteerInCandidate(models.Model):
    volunteer = models.ForeignKey(User)
    candidate = models.ForeignKey(Candidate)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)


class VolunteerGetsCandidateEmailLog(models.Model):
    volunteer = models.ForeignKey(User)
    candidate = models.ForeignKey(Candidate)
    contact = models.ForeignKey(CandidacyContact, null=True)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)


    def save(self, *args, **kwargs):
        creating = self.pk is None
        ## Contact can be none, since a volunteer can
        ## say that she/he contacted the candidate through other means
        if creating and self.contact:
            context = {
                'candidate': self.candidate.name
            }

            send_mail(context, 'contato_novo_com_candidato', to=[self.contact.mail],)
        return super(VolunteerGetsCandidateEmailLog, self).save(*args, **kwargs)


class Coaligacao(models.Model):
    name = models.CharField(max_length=1024, null=True)
    initials = models.CharField(max_length=1024, null=True)
    number = models.CharField(max_length=1024, null=True)
    mark = models.IntegerField(null=True)

class Partido(models.Model):
    name = models.CharField(max_length=1024, null=True)
    initials = models.CharField(max_length=1024, null=True)
    number = models.CharField(max_length=1024, null=True)
    mark = models.IntegerField(null=True)
    coaligacao = models.ForeignKey(Coaligacao, null=True)




##### VOLUNTEERS PART!!!
## I wrote this as part of #MeRepresenta, this means that we haven't needed volunteers doing research on candidates before
## This is why I kept it here until now
## But as I'm coding it I am becoming aware that this could be a good feature to have in the feature, this is why I'm keeping this in
## an inner module, so when I have more time and the need from another NGO to have the volunteers backend
## I can grab it and move it to another application
# from merepresenta.voluntarios.models import VolunteerProfile