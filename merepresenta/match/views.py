from django.views.generic.edit import FormView
from merepresenta.match.forms import QuestionsCategoryForm
from django.shortcuts import render
from merepresenta.match.matrix_builder import MatrixBuilder
import json


class MatchView(FormView):
    template_name = 'match/pergunta.html'
    form_class = QuestionsCategoryForm

    def form_valid(self, form):
        builder = MatrixBuilder()
        categories = form.cleaned_data['categories']
        builder.set_electors_categories(categories)
        r = builder.get_result_as_array()
        context = self.get_context_data()
        context['candidatos'] = json.dumps(r)
        return render(self.request, 'match/resultado.html', context)