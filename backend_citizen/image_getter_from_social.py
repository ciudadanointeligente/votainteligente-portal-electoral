from backend_citizen.tasks import save_image_to_user

def get_image_from_social(backend, strategy, details, response,
        user=None, *args, **kwargs):
    url = None
    if backend.name == 'facebook' and 'id' in response:
        url = "http://graph.facebook.com/%s/picture?type=large" % response['id']

    if backend.name == 'google-oauth2' and 'image' in response:
        url = response['image'].get('url')
        ext = url.split('.')[-1]
    if url:
        try:
            save_image_to_user.delay(url, user)
        except Exception as e:
            pass
