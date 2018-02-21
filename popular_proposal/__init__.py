from importlib import import_module
from django.conf import settings

def _import(class_name):
    if not class_name:
        return None
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

def wizard_forms_field_modifier(wizard_forms_fields):
    func = _import(settings.WIZARD_FORM_MODIFIER)
    if func:
        return func(wizard_forms_fields)
    return wizard_forms_fields

def wizard_previous_form_classes():
    klasses = []
    for class_name in settings.WIZARD_PREVIOUS_CLASSES:
        klasses.append(_import(class_name))

    return klasses

def get_proposal_update_form_class():
    class_name = settings.PROPOSAL_UPDATE_FORM
    try:
        return _import(settings.PROPOSAL_UPDATE_FORM)
    except Exception as e:
        return _import('popular_proposal.forms.forms.UpdateProposalForm')