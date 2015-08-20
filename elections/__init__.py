from writeit.models import WriteItApiInstance, WriteItInstance
from django.conf import settings


def get_writeit_instance():
    api_instance, api_created = WriteItApiInstance.objects.get_or_create(url=settings.WRITEIT_ENDPOINT)

    instance, instance_created = WriteItInstance.objects.get_or_create(api_instance=api_instance,
                                                                       name=settings.WRITEIT_NAME,
                                                                       url=settings.INSTANCE_URL
                                                                       )
    return instance
