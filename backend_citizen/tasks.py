from votai_utils.celery import app
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
import urllib2

def image_getter(url):
    
    img_temp = NamedTemporaryFile(delete=True)
    img_temp.write(urllib2.urlopen(url).read())
    img_temp.flush()
    return File(img_temp)


@app.task
def save_image_to_user(url, user):
    f = image_getter(url)
    user.profile.image = f
    user.profile.image.save(user.username, f)