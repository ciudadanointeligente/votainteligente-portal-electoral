
from django.core.files.temp import NamedTemporaryFile
from django.core.files.images import ImageFile
import urllib2
from django.core.files.storage import get_storage_class
from django.core.files.storage import default_storage
from mimetypes import guess_extension
from django.contrib.sites.models import Site
from elections.models import Candidate
import codecs


def save_candidate_image_locally(c, url):
    current_site = Site.objects.get_current()
    img_temp = NamedTemporaryFile(delete=True)
    try:
        downloaded_image = urllib2.urlopen(url)
    except:
        print(c.name, c.election)
        # c.image = None
        # c.save()
        return
    d = downloaded_image.read()
    img_temp.write(d)
    img_temp.flush()
    i = ImageFile(img_temp.file)
    storage = get_storage_class()()
    data = i.read()
    extension = guess_extension(downloaded_image.info().type)
    file_name = u'candidatos/' + c.id + u'-' + c.election.slug + extension
    path = default_storage.save(file_name, i)
    
    url = u'http://' + current_site.domain + '/cache/' + file_name
    c.image = url
    c.save()

def process_all_candidates():
    current_site = Site.objects.get_current()
    for c in Candidate.objects.all()\
            .exclude(image__isnull=True)\
            .exclude(image__exact='')\
            .exclude(image__icontains=current_site.domain):
        save_candidate_image_locally(c, c.image)
    


def process_photo_csv():
    reader = codecs.open("photos.csv", 'r', encoding='utf-8')
    reader.next()
    for line in reader:
        row = line.split(u',')
        candidate_name = row[1].title().strip()
        image_url = row[2].strip()
        if not candidate_name:
            continue
        if not image_url:
            continue
        try:
            c = Candidate.objects.get(name=candidate_name)
            save_candidate_image_locally(c, image_url)
        except:
            print u'No encontrado:' + candidate_name

