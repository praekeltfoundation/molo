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
            user.is_staff = True
            user.is_superuser = True
            user.save()
        else:
            user.is_staff = False
            user.is_superuser = False
            user.save()
            return None

        return user
