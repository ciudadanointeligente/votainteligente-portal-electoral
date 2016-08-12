# coding=utf-8
from django.contrib.sites.models import Site
from django.contrib.staticfiles.templatetags.staticfiles import static


class OGPMixin(object):
    ogp_enabled = True

    def ogp_title(self):
        return u'{} en VotaInteligente'.format(unicode(self))

    def ogp_type(self):
        return 'website'

    def ogp_url(self):
        site = Site.objects.get_current()
        url = "http://%s%s" % (site.domain,
                               self.get_absolute_url())
        return url

    def ogp_image(self):
        site = Site.objects.get_current()
        url = "http://%s%s" % (site.domain,
                               static('img/logo_vi_og.jpg'))
        return url
