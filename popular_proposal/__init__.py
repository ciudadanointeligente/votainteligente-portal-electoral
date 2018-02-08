from importlib import import_module
from django.conf import settings

def get_model_from(class_name):
    m, k = class_name.rsplit('.', 1)
    mod = import_module(m)
    return getattr(mod, k)

def get_authority_model():
    class_name = "elections.models.Candidate"
    return get_model_from(class_name)

def get_proposal_adapter_model():
    class_name = "proposals_for_votainteligente.models.ProposalsAdapter"
    return get_model_from(class_name)

def send_mail(*args, **kwargs):
    mail_sender = get_model_from('votainteligente.send_mails.send_mail')
    mail_sender(*args, **kwargs)

def send_mails_to_staff(*args, **kwargs):
    mail_sender = get_model_from('votainteligente.send_mails.send_mails_to_staff')
    mail_sender(*args, **kwargs)