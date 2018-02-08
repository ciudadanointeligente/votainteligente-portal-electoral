from importlib import import_module
from django.conf import settings

def get_model_from(class_name):
    m, k = class_name.rsplit('.', 1)
    mod = import_module(m)
    return getattr(mod, k)

def get_authority_model():
    class_name = settings.AUTHORITY_MODEL
    return get_model_from(class_name)

def get_proposal_adapter_model():
    class_name = settings.PROPOSALS_ADAPTER
    return get_model_from(class_name)

def send_mail(*args, **kwargs):
    mail_sender = get_model_from(settings.MAIL_SENDER_FUNCTION)
    mail_sender(*args, **kwargs)

def send_mails_to_staff(*args, **kwargs):
    mail_sender = get_model_from(settings.MAIL_TO_STAFF_SENDER_FUNCTION)
    mail_sender(*args, **kwargs)