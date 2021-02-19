from django.contrib.auth import get_user_model
from molo.core.backends import MoloModelBackend


UserModel = get_user_model()


class MoloProfilesModelBackend(MoloModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)

        if username is not None and request is not None:
            try:
                site = request._wagtail_site
                user = UserModel.objects.get(
                    profile__migrated_username=username,
                    profile__site=site)
                username = user.username
            except UserModel.DoesNotExist:
                UserModel().set_password(password)

        return super(MoloProfilesModelBackend, self).authenticate(
            request=request, username=username, password=password, **kwargs)
