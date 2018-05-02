# coding=utf-8
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from agenda.models import Activity


class ActivityForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.content_object = kwargs.pop('content_object', None)
        super(ActivityForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        activity = super(ActivityForm, self).save(commit=commit)
        if commit:
            activity.content_object = self.content_object
            activity.save()
        return activity

    class Meta:
        model = Activity
        fields = ['date', 'url', 'description', 'location', 'background_image']
        labels = {'date': _(u"Fecha"),
                  'url': _(u"Link a tu actividad, puede ser al evento en Facebook"),
                  'description': _(u"Descripción de tu actividad"),
                  'location': _(u"El lugar donde se realizará esta actividad"),
                  "background_image": _(u"Imagen para promocionar tu actividad")
                 }
