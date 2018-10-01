# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic.detail import DetailView
from elections.models import Area
from django.utils.text import slugify
from django.views.generic.base import RedirectView
from django.core.urlresolvers import reverse


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
        context['all_areas'] = Area.objects.all().order_by('name')
        return context


class ColigacoesInitialRedirect(RedirectView):
    def get_redirect_url(self):
        a = Area.objects.all().order_by('name').first()
        return reverse('coligacoes', kwargs={'slug': a.slug})
