from django.views.generic import View


class EmbeddedViewBase(View):
    layout = 'base.html'
    embedded_layout = 'embedded_base.html'
    is_embedded = False

    def get_context_data(self, * args, **kwargs):
        context = super(EmbeddedViewBase, self).get_context_data(* args, **kwargs)
        if self.is_embedded:
            self.layout = self.embedded_layout
        context['layout'] = self.layout
        context['is_embedded'] = self.is_embedded
        return context
