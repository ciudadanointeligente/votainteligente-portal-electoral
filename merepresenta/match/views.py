from django.views.generic.edit import FormView
from django.http import JsonResponse
from django.views import View
from merepresenta.match.forms import QuestionsCategoryForm
from merepresenta.models import QuestionCategory, Candidate, LGBTQDescription
from django.shortcuts import render
from merepresenta.match.matrix_builder import MatrixBuilder
import json
from django.core.cache import cache
from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy


class MatchQuestionCategoryBase(FormView):
    form_class = QuestionsCategoryForm

    def form_valid(self, form):
        # builder = MatrixBuilder()
        categories = form.cleaned_data['categories']
        # builder.set_electors_categories(categories)
        # r = builder.get_result_as_array()
        context = self.get_context_data()
        context['area'] = form.cleaned_data['area']
        context['categories'] = categories
        election_types_cache_key = 'election_types'
        election_types = cache.get(election_types_cache_key)
        if election_types is None:
            election_types = [{'id': k, 'label': v} for k, v in Candidate.get_possible_election_kinds().items()]
            cache.set(election_types_cache_key, election_types)

        context['election_types'] = election_types
        lgbt_descriptions_cache_key = 'lgbt_descriptions_'
        lgbt_descriptions = cache.get(lgbt_descriptions_cache_key)
        if lgbt_descriptions is None:
            lgbt_descriptions = [{'id': "lgbt_" + str(lgbt_desc.id),
                                  'label': lgbt_desc.name}  for lgbt_desc in LGBTQDescription.objects.all()]
            cache.set(lgbt_descriptions_cache_key, lgbt_descriptions)
        context['lgbt_descriptions'] = lgbt_descriptions
        return render(self.request, self.success_template, context)
    
class MatchView(MatchQuestionCategoryBase):
    template_name = 'match/pergunta.html'
    success_template = 'match/resultado_ajax.html'

    def dispatch(self, *args, **kwargs):
        if not getattr(settings, 'ELEITOR_WORKING', True):
            return HttpResponseRedirect(reverse_lazy('volunteer_index'))
        return super(MatchView, self).dispatch(*args, **kwargs)

class MatchSecretView(MatchQuestionCategoryBase):
    template_name = 'match/pergunta_secret.html'
    success_template = 'match/resultado_ajax.html'

class MatchResultView(MatchQuestionCategoryBase):
    template_name = 'match/pergunta.html'
    success_template = 'match/resultado_ajax.html'


class MatchResultAjaxView(View):
    def post(self, request, *args, **kwargs):
        categories = dict(request.POST)['categories[]']
        categories = QuestionCategory.objects.filter(id__in=categories)
        builder = MatrixBuilder()
        builder.set_electors_categories(categories)
        r = builder.get_result_as_array()
        return JsonResponse(json.dumps(r), safe=False)
        
