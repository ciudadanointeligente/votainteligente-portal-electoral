
from django.views.generic import DetailView
from medianaranja2.models import SharedResult
from django.contrib.contenttypes.models import ContentType
from elections.models import QuestionCategory
from elections.models import Candidate
from medianaranja2.forms import ShareForm
from django.views.generic.edit import CreateView
from organization_profiles.models import OrganizationTemplate
from django.http import HttpResponse
from medianaranja2.forms import MediaNaranjaOnlyProposals, MediaNaranjaWizardForm, MediaNaranjaNoQuestionsWizardForm



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


class ShareMyResultPlzBase(CreateView):
    form_class = ShareForm
    template_name = 'medianaranja2/create_share.html'

    def get_form_kwargs(self):
        kwargs = super(ShareMyResultPlzBase, self).get_form_kwargs()
        kwargs['content_type'] = ContentType.objects.get_for_model(self.shared_object_class)
        return kwargs

class ShareMyResultPlz(ShareMyResultPlzBase):
    shared_object_class = Candidate

class ShareMyResultOrgPlz(ShareMyResultPlzBase):
    shared_object_class = OrganizationTemplate


class SharedResultOGImageView(DetailView):
    model = SharedResult
    slug_url_kwarg = 'identifier'
    slug_field = 'identifier'

    def render_to_response(self, context, **response_kwargs):
        im = self.object.get_shared_image()
        response = HttpResponse( content_type="image/png")
        im.save(response, "PNG")
        return response

def get_medianaranja_view(*args, **kwargs):
    from django.conf import settings
    from constance import config
    if settings.MEDIA_NARANJA_QUESTIONS_ENABLED:
        if not QuestionCategory.objects.exists():
            view = MediaNaranjaNoQuestionsWizardForm.as_view()
        else:
            view = MediaNaranjaWizardForm.as_view()
    else:
        view = MediaNaranjaOnlyProposals.as_view()

    try:
        if config.PRUEBAS_DE_CARGA_MEDIA_NARANJA:
            view = csrf_exempt(view)
    except:
        pass
    return view(*args, **kwargs)