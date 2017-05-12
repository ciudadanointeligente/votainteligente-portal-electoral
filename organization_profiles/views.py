# coding=utf-8
from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.contrib.auth.models import User
from django.http import HttpResponse
from pybars import Compiler
import os
import codecs
from django.core.files import File
from organization_profiles.models import BASIC_FIELDS


def read_template_as_string(path, file_source_path=__file__):
    script_dir = os.path.dirname(file_source_path)
    result = ''
    with codecs.open(os.path.join(script_dir, 'templates', path), 'r', encoding='utf8') as f:
        result = f.read()
    return result


class HandleBarsResponse(HttpResponse):
    def __init__(self, source, obj, **kwargs):
        compiler = Compiler()
        template = compiler.compile(source)
        content = template(obj)
        super(HandleBarsResponse, self).__init__(content=content, **kwargs)


class OrganizationDetailView(DetailView):
    model = User
    slug_field = 'username'
    template_name = 'organization_detail_view.hbs'
    response_class = HandleBarsResponse

    def create_context_based_on_organization_template(self, context):
        for field in BASIC_FIELDS:
            value = getattr(self.object.organization_template, field)
            if isinstance(value, File) and value:
                value = value.url
            context[field] = value
        return context

    def render_to_response(self, context, **kwargs):
        context = self.create_context_based_on_organization_template(context)
        if self.object.organization_template.content:
            return self.response_class(self.object.organization_template.content,
                                       context)
        source = read_template_as_string(self.template_name)
        return self.response_class(source,
                                   context)
