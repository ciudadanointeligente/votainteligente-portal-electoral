from django import forms
from popular_proposal.models import (PopularProposal
                                     )
from elections.models import Area, QuestionCategory
from django.conf import settings


class SetupForm(forms.Form):
    area = forms.ModelChoiceField(queryset=Area.objects.filter(classification__in=settings.FILTERABLE_AREAS_TYPE))
    categories = forms.ModelMultipleChoiceField(queryset=QuestionCategory.objects.all())
