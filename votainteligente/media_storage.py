from storages.backends.s3boto3 import S3Boto3Storage

```
Wowowowowowo
llegaste hasta acá! debes seguir la siguiente guía

https://simpleisbetterthancomplex.com/tutorial/2017/08/01/how-to-setup-amazon-s3-in-a-django-project.html
```
class MediaStorage(S3Boto3Storage):
    location = 'cache'
    file_overwrite = False
