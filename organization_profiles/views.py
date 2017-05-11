# coding=utf-8
from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.contrib.auth.models import User
# >>> from pybars import Compiler
# >>> compiler = Compiler()
# >>> source = u"<h1>{{name}}</h1>"
# >>> template = compiler.compile(source)
# >>> print(template({"name": "Fiera"}))
# <h1>Fiera</h1>
# se puede sacar información desde acá
# https://github.com/ciudadanointeligente/deldichoalhecho/blob/master/ddah_web/views.py#L11-L59


class OrganizationDetailView(DetailView):
    model = User
    slug_field = 'username'
    template_name = 'organization_detail_view.html'
