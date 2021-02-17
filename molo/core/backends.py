from django.contrib.auth.models import Group
from django_cas_ng.backends import CASBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import PermissionDenied

from molo.profiles.models import UserProfile

UserModel = get_user_model()


class MoloModelBackend(ModelBackend):

    def authenticate(
            self, request, username=None, password=None, *args, **kwargs):

        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if request is not None:
            try:
                user = UserModel._default_manager.get_by_natural_key(username)
                if user.is_superuser:
                    UserProfile.objects.get(user=user)
                else:
                    UserProfile.objects.get(
                        user=user, site=request._wagtail_site)
            except UserProfile.DoesNotExist:
                raise PermissionDenied
            except UserModel.DoesNotExist:
                UserModel().set_password(password)

        return super(MoloModelBackend, self).authenticate(
            request=request, username=username, password=password, **kwargs)


class MoloCASBackend(CASBackend):

    def authenticate(self, request, ticket, service):
        user = super(
            MoloCASBackend, self).authenticate(request, ticket, service)
        if user is None:
            return None

        if 'attributes' in request.session \
            and 'has_perm' in request.session['attributes']\
                and request.session['attributes']['has_perm'] == 'True':
            site = request._wagtail_site
            if request.session['attributes']['is_admin'] == 'True':
                user.email = request.session['attributes']['email']
                user.is_staff = True
                user.is_superuser = True
                user.save()
            else:
                wagtail_login_only_group = Group.objects.filter(
                    name='Wagtail Login Only').first()
                if wagtail_login_only_group and not user.groups.exists():
                    user.groups.add(wagtail_login_only_group)

                elif not user.profile.admin_sites.filter(
                        pk=site.pk).exists():
                    return None

                """
                TODO: Handle case where Moderator group does not exist.
                We need to log this or find ways of notifying users that
                the moderator group was removed or renamed.
                There isn't much we can do about this case though.
                """
        else:
            user.is_staff = False
            user.is_superuser = False
            user.save()
            return None

        return user
