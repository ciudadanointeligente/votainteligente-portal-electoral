# coding=utf-8
from django.db import models
from elections.models import Candidate
from popular_proposal.models import PopularProposal
from picklefield.fields import PickledObjectField
from django.contrib.contenttypes.models import ContentType
import uuid
from PIL import Image, ImageDraw, ImageFont
from django.core.urlresolvers import reverse
from io import BytesIO
from django.contrib.sites.models import Site


class ReadingGroup(models.Model):
    name = models.CharField(max_length=512)
    candidates = models.ManyToManyField(Candidate, related_name='groups')

    def get_proposals(self, elections=None):
        qs = PopularProposal.ordered.all()
        candidates = self.candidates
        if elections is not None:
            candidates = candidates.filter(elections__in=elections)
        qs = qs.filter(commitments__candidate__in=candidates.all())
        qs = qs.order_by('-num_likers')
        return qs


class SharedResult(models.Model):
    identifier = models.UUIDField(default=uuid.uuid4)
    data = PickledObjectField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse('medianaranja2:share', kwargs={'identifier': self.identifier})

    def get_shared_image(self):
        plantilla = Image.open('votai_general_theme/static/img/plantilla_org.png')

        montserrat_n_propuesta = ImageFont.truetype("votai_general_theme/static/fonts/Montserrat-Bold.ttf", 16)
        arvo_titulo = ImageFont.truetype("votai_general_theme/static/fonts/Arvo-Bold.ttf", 60)
        montserrat_autor = ImageFont.truetype("votai_general_theme/static/fonts/Montserrat-Bold.ttf", 22)
        bg_color = "#FF00FF"
        output = BytesIO()
        output.seek(0)
        h = bg_color.lstrip('#')
        rgb_color = tuple(int(h[i:i+2], 16) for i in (0, 2 ,4))
        rgb_color = rgb_color
        base = Image.new('RGBA',(1200,630),rgb_color)
        
        base.paste(plantilla, (0,0), plantilla)
        return base

    def ogp_image(self):
        site = Site.objects.get_current()
        image_url = reverse('medianaranja2:og_image',
                            kwargs={'identifier': self.identifier})
        url = "https://%s%s" % (site.domain,
                               image_url)
        return url