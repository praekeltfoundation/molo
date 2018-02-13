from molo.profiles.forms import EditProfileForm


def get_profile_data(request):
    username = ''
    alias = ''
    date_of_birth = ''
    mobile_number = ''
    if request.user.is_authenticated():
        user = request.user
        profile = user.profile
        username = user.username
        if profile.alias:
            alias = profile.alias
        else:
            alias = 'Anonymous'
        date_of_birth = profile.date_of_birth
        mobile_number = profile.mobile_number
    edit_profile_form = EditProfileForm(
        initial={
            'username': username,
            'alias': alias,
            'mobile_number': mobile_number,
            'date_of_birth': date_of_birth
        }
    )
    return {
        'username': username,
        'alias': alias,
        'date_of_birth': date_of_birth,
        'mobile_number': mobile_number,
        'edit_profile_form': edit_profile_form
    }
