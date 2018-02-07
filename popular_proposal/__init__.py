from importlib import import_module


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