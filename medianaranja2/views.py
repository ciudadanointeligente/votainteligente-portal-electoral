
from django.views.generic import DetailView
from medianaranja2.models import SharedResult
from django.views.generic.base import RedirectView
from django.contrib.contenttypes.models import ContentType
from elections.models import Candidate


class ShareYourResult(DetailView):
    model = SharedResult
    slug_url_kwarg = 'identifier'
    slug_field = 'identifier'
    template_name = 'medianaranja2/comparte_resultado.html'

    def get_context_data(self, **kwargs):
        context = super(ShareYourResult, self).get_context_data(**kwargs)
        context['shared_object'] = self.object.data['object_id']
        context['percentage'] = self.object.data['percentage']
        return context

class ShareMyResultPlz(RedirectView):
    shared_object_class = Candidate

    def post(self, request):
        object_id = request.POST.get('object_id')
        percentage = request.POST.get('percentage')
        content_type = ContentType.objects.get_for_model(Candidate)
        self.object = SharedResult.objects.create(data={'object_id': object_id, 'percentage': float(percentage)},
                                                  content_type=content_type)
        return super(ShareMyResultPlz, self).post(request)

    def get_redirect_url(self, *args, **kwargs):
        return self.object.get_absolute_url()