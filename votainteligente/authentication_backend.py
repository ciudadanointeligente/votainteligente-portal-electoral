from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.forms import ValidationError
from django.core.validators import validate_email


class VotaIAuthenticationBackend(ModelBackend):
    """
    Authenticates against settings.AUTH_USER_MODEL.
    """

    def authenticate(self, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        try:
            try:
                validate_email(username)
                kwargs = {'email': username}
            except ValidationError:
                kwargs = {'username': username}
            user = UserModel._default_manager.filter(**kwargs).first()
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            UserModel().set_password(password)
        else:
            if user and user.check_password(password) and self.user_can_authenticate(user):
                return user
