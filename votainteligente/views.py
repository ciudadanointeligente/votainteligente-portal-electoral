from django.views.generic import TemplateView


class HomeViewBase(TemplateView):
	template_name='index.html'
