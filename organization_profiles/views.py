# coding=utf-8
from django.views.generic.detail import DetailView
from django.contrib.auth.models import User
from django.http import Http404, HttpResponse
from pybars import Compiler
import os
import codecs
from django.core.files import File
from organization_profiles.models import BASIC_FIELDS
from django.template.loader import get_template
from django.views.generic.edit import UpdateView
from organization_profiles.forms import OrganizationTemplateForm
from django.core.urlresolvers import reverse
from django.views.generic.edit import UpdateView
from organization_profiles.models import ExtraPage
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse


def read_template_as_string(path, file_source_path=__file__):
    script_dir = os.path.dirname(file_source_path)
    result = ''
    with codecs.open(os.path.join(script_dir, 'templates', path), 'r', encoding='utf8') as f:
        result = f.read()
    return result


class HandleBarsResponse(HttpResponse):
    def __init__(self, source, obj, **kwargs):
        compiler = Compiler()
        base_template = compiler.compile(u'<!DOCTYPE html><html lang="es">{{> head}}<body><div>{{> nav}}<div>{{> content}}</div></div>{{> footer}}</body></html>')
        head = compiler.compile(get_template("_head.html").render({}))
        footer = compiler.compile(get_template("_footer.html").render({}))
        content_template = compiler.compile(source)
        nav = compiler.compile(get_template("_navbar.html").render(obj))
        everything = base_template(obj, partials={"content": content_template,
                                                  "head": head,
                                                  "nav": nav,
                                                  "footer": footer})
        super(HandleBarsResponse, self).__init__(content=everything, **kwargs)


class OrganizationDetailView(DetailView):
    model = User
    slug_field = 'username'
    template_name = 'organization_detail_view.hbs'
    context_object_name = 'organization'
    response_class = HandleBarsResponse

    def create_context_based_on_organization_template(self, context):

        context['extra_pages'] = []
        for extra_page in self.object.organization_template.extra_pages.all():
            context['extra_pages'].append({"title": extra_page.title,
                                           "slug": extra_page.slug,
                                           "content": extra_page.content_markdown})
        context['proposals'] = []
        for proposal in self.object.proposals.all():
            context['proposals'].append(proposal)

        context['sponsorships'] = []
        for sponsorship in self.object.proposallike_set.all():
            context['sponsorships'].append(sponsorship)

        for field in BASIC_FIELDS:
            value = getattr(self.object.organization_template, field)
            if isinstance(value, File) and value:
                value = value.url
            context[field] = value
        return context

    def render_to_response(self, context, **kwargs):
        context = self.create_context_based_on_organization_template(context)
        context['user'] = self.request.user
        context['is_owner'] = self.request.user == self.object
        if context['is_owner']:
          context['update_url'] = reverse('organization_profiles:update')
          context['create_proposal_url'] = reverse('popular_proposals:propose_wizard_full_without_area')
        if self.object.organization_template.content:
            return self.response_class(self.object.organization_template.content,
                                       context)
        source = read_template_as_string(self.template_name)
        return self.response_class(source, context)


from django.contrib.auth.mixins import LoginRequiredMixin


class OrganizationTemplateUpdateView(LoginRequiredMixin, UpdateView):
    form_class = OrganizationTemplateForm
    template_name = 'backend_organization/update_my_profile.html'

    def get_object(self):
        if not self.request.user.profile.is_organization:
            raise Http404()
        return self.request.user.organization_template

    def get_success_url(self):
        return reverse('organization_profiles:update')


class ExtraPageUpdateView(LoginRequiredMixin, UpdateView):
    model = ExtraPage
    fields = ['title', 'content']
    template_name = "backend_organization/update_extrapage.html"

    def get_object(self):
        extra_page = super(ExtraPageUpdateView, self).get_object()
        if extra_page.template.organization != self.request.user:
            raise Http404()
        return extra_page

    def get_success_url(self):
        return reverse('organization_profiles:update_extrapage', kwargs={'pk':self.object.pk})
