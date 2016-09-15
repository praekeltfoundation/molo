from django.contrib.auth.models import Group
from django_cas_ng.backends import CASBackend


class MoloCASBackend(CASBackend):

    def authenticate(self, ticket, service, request):
        user = super(
            MoloCASBackend, self).authenticate(ticket, service, request)
        if user is None:
            return None

        if 'attributes' in request.session \
            and 'has_perm' in request.session['attributes']\
                and request.session['attributes']['has_perm'] == 'True':
            if request.session['attributes']['is_admin'] == 'True':
                user.is_staff = True
                user.is_superuser = True
                user.save()
            else:
                moderator_group = Group.objects.filter(
                    name='Moderators').first()
                if moderator_group:
                    user.groups.add(moderator_group)
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
