# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from elections.models import Candidate
import uuid
from picklefield.fields import PickledObjectField
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from votai_utils.send_mails import send_mail
from backend_candidate.models import CandidacyContact
import time


class ProposalSuggestionForIncremental(models.Model):
    incremental = models.ForeignKey('IncrementalsCandidateFilter', related_name="suggestions")
    proposal = models.ForeignKey('popular_proposal.PopularProposal', related_name="suggested_proposals")
    summary = models.TextField(default=u"", blank=True)
    sent = models.BooleanField(default=False)


class CandidateIncremental(models.Model):
    suggestion = models.ForeignKey('IncrementalsCandidateFilter', null=True, on_delete=models.SET_NULL)
    candidate = models.ForeignKey(Candidate)
    identifier = models.UUIDField(default=uuid.uuid4)
    used = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True,
                                   blank=True,
                                   null=True)
    updated = models.DateTimeField(auto_now=True,
                                   blank=True,
                                   null=True)

    @property
    def _formset_class(self):
        proposals = []
        summaries = []
        for p in self.suggestion.suggested_proposals.order_by('id'):
            proposals.append(p)
            summaries.append(self.suggestion.suggestions.get(proposal=p).summary)
        from suggestions_for_candidates.forms import get_multi_commitment_forms
        return get_multi_commitment_forms(self.candidate, proposals, summaries)

    @property
    def formset(self):
        formset = self._formset_class()
        return formset

    def get_absolute_url(self):
        return reverse("suggestions_for_candidates:commit_to_suggestions", kwargs={"identifier": self.identifier})

    def send_mail(self, sleep):
        context = self.suggestion.get_context_for_candidate(self.candidate)
        context['formset'] = self.formset
        context['candidate_incremental'] = self
        for candidacy in self.candidate.candidacy_set.all():
            context['candidacy'] = candidacy
            if candidacy.user.last_login is None:
                try:
                    contact = candidacy.user.candidacy_contact
                    context['contact'] = contact
                except CandidacyContact.DoesNotExist:
                    pass
            subject = None
            if self.suggestion and self.suggestion.subject:
                subject = self.suggestion.subject
            send_mail(context, 'suggestions_for_candidates',
                  subject=subject,
                  to=[candidacy.user.email])
            time.sleep(sleep)

class IncrementalsCandidateFilter(models.Model):
    name = models.CharField(max_length=12288,
                            null=True,
                            blank=True)
    subject = models.CharField(max_length=256,
                               null=True,
                               blank=True)
    text = models.TextField(blank=True)
    filter_qs = PickledObjectField()
    exclude_qs = PickledObjectField()
    suggested_proposals = models.ManyToManyField('popular_proposal.PopularProposal',
                                                 through=ProposalSuggestionForIncremental)

    class Meta:
        verbose_name = _(u"Filtro de propuestas para candidatos")
        verbose_name_plural = _(u"Filtros de propuestas para candidatos")

    def get_candidates(self):
        return Candidate.objects.filter(**self.filter_qs).exclude(**self.exclude_qs)


    def get_mail_context(self):
        return {'proposals': self.suggested_proposals}

    def get_proposals_for_candidate(self, candidate):
        proposals = []
        for p in self.suggested_proposals.all():
            if not candidate.commitments.filter(proposal=p):
                proposals.append(p)
        return proposals

    def get_context_for_candidate(self, candidate):
        return {'candidate': candidate,
                'text': self.text,
                'proposals': self.get_proposals_for_candidate(candidate)}

    def send_mails(self, sleep=0):
        candidates = self.get_candidates()
        for c in candidates:
            candidate_incremental = CandidateIncremental.objects.create(candidate=c,
                                                                        suggestion=self)
            candidate_incremental.send_mail(sleep)
