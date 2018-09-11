from django.views.generic.edit import FormView
from django.http import JsonResponse
from django.views import View
from merepresenta.match.forms import QuestionsCategoryForm
from merepresenta.models import QuestionCategory
from django.shortcuts import render
from merepresenta.match.matrix_builder import MatrixBuilder
import json

class MatchQuestionCategoryBase(FormView):
    form_class = QuestionsCategoryForm

    def form_valid(self, form):
        # builder = MatrixBuilder()
        categories = form.cleaned_data['categories']
        # builder.set_electors_categories(categories)
        # r = builder.get_result_as_array()
        context = self.get_context_data()
        context['categories'] = categories
        return render(self.request, self.success_template, context)
    
class MatchView(MatchQuestionCategoryBase):
    template_name = 'match/pergunta.html'
    success_template = 'match/paso2_explicacion_pautas.html'


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
        