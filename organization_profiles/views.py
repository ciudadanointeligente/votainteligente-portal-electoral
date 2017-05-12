# coding=utf-8
from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.contrib.auth.models import User
from django.http import HttpResponse
from pybars import Compiler
# >>> from pybars import Compiler
# >>> compiler = Compiler()
# >>> source = u"<h1>{{name}}</h1>"
# >>> template = compiler.compile(source)
# >>> print(template({"name": "Fiera"}))
# <h1>Fiera</h1>
# se puede sacar información desde acá
# https://github.com/ciudadanointeligente/deldichoalhecho/blob/master/ddah_web/views.py#L11-L59


class HandleBarsResponse(HttpResponse):
    def __init__(self, source, obj, **kwargs):
        compiler = Compiler()
        template = compiler.compile(source)
        content = template(obj)
        super(HandleBarsResponse, self).__init__(content=content, **kwargs)

class OrganizationDetailView(DetailView):
    model = User
    slug_field = 'username'
    response_class = HandleBarsResponse

    def render_to_response(self, context, **kwargs):
        return self.response_class(self.object.organization_template.content,
                                   context)
