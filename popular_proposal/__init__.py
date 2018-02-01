from importlib import import_module


def get_authority_model():
    class_name = "elections.models.Candidate"
    m, k = class_name.rsplit('.', 1)
    mod = import_module(m)
    return getattr(mod, k)