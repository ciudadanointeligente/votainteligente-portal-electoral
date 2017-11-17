# coding=utf-8
from django.db import models
from elections.models import Candidate
from popular_proposal.models import PopularProposal
from picklefield.fields import PickledObjectField
from django.contrib.contenttypes.models import ContentType
import uuid
from PIL import Image, ImageDraw, ImageFont, ImageOps
from django.core.urlresolvers import reverse
from io import BytesIO
from django.contrib.sites.models import Site
import textwrap


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

    def get_text_for_image(self):
        montserrat_n_propuesta = ImageFont.truetype("votai_general_theme/static/fonts/Montserrat-Bold.ttf", 34)
        txt = Image.new('RGBA', (1200,630), (255,255,255,0))

        d = ImageDraw.Draw(txt)
        
        lines = textwrap.wrap(self.object.name, width=29)
        max_lines = 2
        if len(lines) > max_lines:
            last_line = lines[max_lines - 1]
            lines = lines[0:max_lines]
            lines[max_lines - 1] = last_line

        title = '\n'.join(lines)

        rgb_color = (255,255,255)
        d.multiline_text((68,302), title, font=montserrat_n_propuesta, fill=rgb_color)
        return txt

    def get_shared_image(self):
        
        base = Image.new('RGBA',(1200,630),(254,199,13))

        bg_color = "#FF00FF"
        output = BytesIO()
        output.seek(0)
        h = bg_color.lstrip('#')
        
        img = Image.open(self.object.image)
        bigsize = (396, 396)
        img = img.resize(bigsize, Image.ANTIALIAS)

        base.paste(img,(784,96))
        plantilla = Image.open('votai_general_theme/static/img/plantilla_naranja.png').convert("RGBA")
        base.paste(plantilla, (0,0), plantilla)
        text = self.get_text_for_image()

        out = Image.alpha_composite(base, text)

        return out

    def ogp_image(self):
        site = Site.objects.get_current()
        image_url = reverse('medianaranja2:og_image',
                            kwargs={'identifier': self.identifier})
        url = "//%s%s" % (site.domain,
                               image_url)
        return url

    @property
    def object(self):
        return self.content_type.get_object_for_this_type(id=self.data["object_id"])