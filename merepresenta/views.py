# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic.detail import DetailView
from elections.models import Area
from django.utils.text import slugify


class ColigacoesPerAreaView(DetailView):
    template_name = 'merepresenta/coligacoes.html'
    context_object_name = 'area'
    model = Area

    def get_context_data(self, *args, **kwargs):
        context = super(ColigacoesPerAreaView, self).get_context_data(*args, **kwargs)
        coligacoes = {}
        for c in self.object.coligacoes.all():
            if c.classification not in coligacoes.keys():
                coligacoes[c.classification] = []
            coligacoes[c.classification].append(c)
        context['coligacoes'] = coligacoes
        context['all_areas'] = Area.objects.all()
        return context

