from importlib import import_module
from django.conf import settings

def _import(class_name):
    m, k = class_name.rsplit('.', 1)
    mod = import_module(m)
    return getattr(mod, k)

def get_authority_model():
    class_name = settings.AUTHORITY_MODEL
    return _import(class_name)

def get_proposal_adapter_model():
    class_name = settings.PROPOSALS_ADAPTER
    return _import(class_name)

def send_mail(*args, **kwargs):
    mail_sender = _import(settings.MAIL_SENDER_FUNCTION)
    mail_sender(*args, **kwargs)

def send_mails_to_staff(*args, **kwargs):
    mail_sender = _import(settings.MAIL_TO_STAFF_SENDER_FUNCTION)
    mail_sender(*args, **kwargs)

def default_filterset_class():
    return _import(settings.DEFAULT_FITERSET_CLASS)