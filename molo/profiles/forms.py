from django.utils import timezone

import re

from django import forms
from django.forms.extras.widgets import SelectDateWidget
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from wagtail.wagtailcore.models import Site
from molo.profiles.models import UserProfile, UserProfilesSettings

from phonenumber_field.formfields import PhoneNumberField

User = get_user_model()

REGEX_PHONE = settings.REGEX_PHONE if hasattr(settings, 'REGEX_PHONE') else \
    r'.*?(\(?\d{3})? ?[\.-]? ?\d{3} ?[\.-]? ?\d{4}.*?'

REGEX_EMAIL = settings.REGEX_EMAIL if hasattr(settings, 'REGEX_PHONE') else \
    r'([\w\.-]+@[\w\.-]+)'


class MoloAuthenticationForm(AuthenticationForm):

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(request=self.request,
                                           username=username,
                                           password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


def get_validation_msg_fragment():
    site = Site.objects.get(is_default_site=True)
    profile_settings = UserProfilesSettings.for_site(site)

    invalid_msg = ''

    if getattr(profile_settings, 'prevent_email_in_username', False) \
            and getattr(profile_settings, 'prevent_phone_number_in_username',
                        False):
        invalid_msg = 'phone number or email address'

    elif getattr(profile_settings, 'prevent_phone_number_in_username', False):
        invalid_msg = 'phone number'

    elif getattr(profile_settings, 'prevent_email_in_username', False):
        invalid_msg = 'email address'

    return invalid_msg


def validate_no_email_or_phone(input):
    site = Site.objects.get(is_default_site=True)
    profile_settings = UserProfilesSettings.for_site(site)

    regexes = []
    if profile_settings.prevent_phone_number_in_username:
        regexes.append(REGEX_PHONE)

    if profile_settings.prevent_email_in_username:
        regexes.append(REGEX_EMAIL)

    for regex in regexes:
        match = re.search(regex, input)
        if match:
            return False

    return True


class RegistrationForm(forms.Form):
    username = forms.RegexField(
        regex=r'^[\w.@+-]+$',
        widget=forms.TextInput(
            attrs=dict(
                required=True,
                max_length=30,
            )
        ),
        label=_("Username"),
        error_messages={
            'invalid': _("This value must contain only letters, "
                         "numbers and underscores."),
        }
    )
    password = forms.RegexField(
        regex=r'^\d{4}$',
        widget=forms.PasswordInput(
            attrs=dict(
                required=True,
                render_value=False,
                type='password',
            )
        ),
        max_length=4,
        min_length=4,
        error_messages={
            'invalid': _("This value must contain only numbers."),
        },
        label=_("PIN")
    )
    email = forms.EmailField(required=False)
    mobile_number = PhoneNumberField(required=False)
    terms_and_conditions = forms.BooleanField(required=True)
    alias = forms.CharField(
        label=_("Display Name"),
        required=False
    )
    date_of_birth = forms.DateField(
        widget=SelectDateWidget(
            years=list(reversed(range(1930, timezone.now().year + 1)))
        ),
        required=False
    )
    gender = forms.CharField(
        label=_("Gender"),
        required=False
    )
    location = forms.CharField(
        label=_("Location"),
        required=False
    )
    education_level = forms.CharField(
        label=_("Education Level"),
        required=False
    )
    next = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        questions = kwargs.pop("questions", [])
        request = kwargs.pop("request", [])
        super(RegistrationForm, self).__init__(*args, **kwargs)
        if not request:
            site = Site.objects.get(is_default_site=True)
            profile_settings = UserProfilesSettings.for_site(site)
        else:
            profile_settings = UserProfilesSettings.for_site(request.site)
        self.fields['mobile_number'].required = (
            profile_settings.mobile_number_required and
            profile_settings.show_mobile_number_field and
            profile_settings.country_code)
        self.fields['email'].required = (
            profile_settings.email_required and
            profile_settings.show_email_field)
        self.fields['alias'].required = (
            profile_settings.activate_display_name and
            profile_settings.capture_display_name_on_reg and
            profile_settings.display_name_required)
        self.fields['date_of_birth'].required = (
            profile_settings.activate_dob and
            profile_settings.capture_dob_on_reg and
            profile_settings.dob_required)
        self.fields['gender'].required = (
            profile_settings.activate_gender and
            profile_settings.capture_gender_on_reg and
            profile_settings.gender_required)
        self.fields['location'].required = (
            profile_settings.activate_location and
            profile_settings.capture_location_on_reg and
            profile_settings.location_required)
        self.fields['education_level'].required = (
            profile_settings.activate_education_level and
            profile_settings.capture_education_level_on_reg and
            profile_settings.activate_education_level_required)

        # Security questions fields are created dynamically.
        # This allows any number of security questions to be specified
        for index, question in enumerate(questions):
            self.fields["question_%s" % index] = forms.CharField(
                label=question.title,
                widget=forms.TextInput(
                    attrs=dict(
                        max_length=150,
                    )
                )
            )
            self.fields["question_%s" % index].required = (
                profile_settings.show_security_question_fields and
                profile_settings.security_questions_required
            )

    def security_questions(self):
        return [
            self[name] for name in filter(
                lambda x: x.startswith('question_'), self.fields.keys()
            )
        ]

    def clean_username(self):
        validation_msg_fragment = get_validation_msg_fragment()

        if User.objects.filter(
                username__iexact=self.cleaned_data['username']
        ).exists():
            raise forms.ValidationError(_("Username already exists."))

        if not validate_no_email_or_phone(self.cleaned_data['username']):
            raise forms.ValidationError(
                _(
                    "Sorry, but that is an invalid username. Please don't use"
                    " your %s in your username." % validation_msg_fragment
                )
            )

        return self.cleaned_data['username']

    def is_valid(self):
        if 'mobile_number' in self.data:
            if not self.data['mobile_number'].startswith('+'):
                site = Site.objects.get(is_default_site=True)
                profile_settings = UserProfilesSettings.for_site(site)
                number = self.data['mobile_number']
                if number:
                    if number.startswith('0'):
                        number = number[1:]
                    number = profile_settings.country_code + \
                        number
                self.data = self.data.copy()
                self.data['mobile_number'] = number
        valid = super(RegistrationForm, self).is_valid()
        return valid

    def clean_alias(self):
        validation_msg_fragment = get_validation_msg_fragment()

        alias = self.cleaned_data['alias']

        if not validate_no_email_or_phone(alias):
            raise forms.ValidationError(
                _(
                    "Sorry, but that is an invalid display name. "
                    "Please don't use your %s in your display name."
                    % validation_msg_fragment
                )
            )

        return alias


class DoneForm(forms.Form):
    date_of_birth = forms.DateField(
        widget=SelectDateWidget(
            years=list(reversed(range(1930, timezone.now().year + 1)))
        )
    )
    alias = forms.CharField(
        label=_("Display Name"),
        required=False
    )
    gender = forms.CharField(
        label=_("Gender"),
        required=False
    )
    location = forms.CharField(
        label=_("Location"),
        required=False
    )
    education_level = forms.CharField(
        label=_("Education Level"),
        required=False
    )

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request", [])
        super(DoneForm, self).__init__(*args, **kwargs)
        if not request:
            site = Site.objects.get(is_default_site=True)
            profile_settings = UserProfilesSettings.for_site(site)
        else:
            profile_settings = UserProfilesSettings.for_site(request.site)
        self.fields['date_of_birth'].required = (
            profile_settings.activate_dob and not
            profile_settings.capture_dob_on_reg and
            profile_settings.dob_required)
        self.fields['alias'].required = (
            profile_settings.activate_display_name and not
            profile_settings.capture_display_name_on_reg and
            profile_settings.display_name_required)
        self.fields['gender'].required = (
            profile_settings.activate_gender and not
            profile_settings.capture_gender_on_reg and
            profile_settings.gender_required)
        self.fields['location'].required = (
            profile_settings.activate_location and not
            profile_settings.capture_location_on_reg and
            profile_settings.location_required)
        self.fields['education_level'].required = (
            profile_settings.activate_education_level and not
            profile_settings.capture_education_level_on_reg and
            profile_settings.activate_education_level_required)


class EditProfileForm(forms.ModelForm):
    alias = forms.CharField(
        label=_("Display Name"),
        required=False
    )
    date_of_birth = forms.DateField(
        widget=SelectDateWidget(
            years=list(reversed(range(1930, timezone.now().year + 1)))
        ),
        required=False
    )
    gender = forms.CharField(
        label=_("Gender"),
        required=False
    )
    location = forms.CharField(
        label=_("Location"),
        required=False
    )
    education_level = forms.CharField(
        label=_("Education Level"),
        required=False
    )
    mobile_number = PhoneNumberField(required=False)
    email = forms.EmailField(required=False)

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request", [])
        super(EditProfileForm, self).__init__(*args, **kwargs)
        if not request:
            site = Site.objects.get(is_default_site=True)
            profile_settings = UserProfilesSettings.for_site(site)
        else:
            profile_settings = UserProfilesSettings.for_site(request.site)
        self.fields['mobile_number'].required = (
            profile_settings.mobile_number_required and
            profile_settings.show_mobile_number_field and
            profile_settings.country_code)
        self.fields['email'].required = (
            profile_settings.email_required and
            profile_settings.show_email_field)
        self.fields['alias'].required = (
            profile_settings.activate_display_name and
            profile_settings.display_name_required)
        self.fields['date_of_birth'].required = (
            profile_settings.activate_dob and
            profile_settings.dob_required)
        self.fields['gender'].required = (
            profile_settings.activate_gender and
            profile_settings.gender_required)
        self.fields['location'].required = (
            profile_settings.activate_location and
            profile_settings.location_required)
        self.fields['education_level'].required = (
            profile_settings.activate_education_level and
            profile_settings.activate_education_level_required)

    class Meta:
        model = UserProfile
        fields = ['alias', 'date_of_birth', 'mobile_number',
                  'gender', 'location', 'education_level']

    def clean_alias(self):
        validation_msg_fragment = get_validation_msg_fragment()

        alias = self.cleaned_data['alias']

        if not validate_no_email_or_phone(alias):
            raise forms.ValidationError(
                _(
                    "Sorry, but that is an invalid display name. "
                    "Please don't use your %s in your display name."
                    % validation_msg_fragment
                )
            )

        return alias

    def is_valid(self):
        if 'mobile_number' in self.data:
            if not self.data['mobile_number'].startswith('+'):
                site = Site.objects.get(is_default_site=True)
                profile_settings = UserProfilesSettings.for_site(site)
                number = self.data['mobile_number']
                if number:
                    if number.startswith('0'):
                        number = number[1:]
                    number = profile_settings.country_code + \
                        number
                self.data = self.data.copy()
                self.data['mobile_number'] = number
        valid = super(EditProfileForm, self).is_valid()
        return valid


class ProfilePasswordChangeForm(forms.Form):
    old_password = forms.RegexField(
        regex=r'^\d{4}$',
        widget=forms.PasswordInput(
            attrs=dict(
                required=True,
                render_value=False,
                type='password',
            )
        ),
        max_length=4, min_length=4,
        error_messages={'invalid': _("This value must contain only  \
         numbers.")},
        label=_("Old Password")
    )
    new_password = forms.RegexField(
        regex=r'^\d{4}$',
        widget=forms.PasswordInput(
            attrs=dict(
                required=True,
                render_value=False,
                type='password',
            )
        ),
        max_length=4,
        min_length=4,
        error_messages={'invalid': _("This value must contain only  \
         numbers.")},
        label=_("New Password")
    )
    confirm_password = forms.RegexField(
        regex=r'^\d{4}$',
        widget=forms.PasswordInput(
            attrs=dict(
                required=True,
                render_value=False,
                type='password',
            )
        ),
        max_length=4,
        min_length=4,
        error_messages={
            'invalid': _("This value must contain only numbers."),
        },
        label=_("Confirm Password")
    )

    def clean(self):
        new_password = self.cleaned_data.get('new_password', None)
        confirm_password = self.cleaned_data.get('confirm_password', None)
        if (new_password and confirm_password and
                (new_password == confirm_password)):
            return self.cleaned_data
        else:
            raise forms.ValidationError(_('New passwords do not match.'))


class ForgotPasswordForm(forms.Form):
    username = forms.RegexField(
        regex=r'^[\w.@+-]+$',
        widget=forms.TextInput(
            attrs=dict(
                required=True,
                max_length=30,
            )
        ),
        label=_("Username"),
        error_messages={
            'invalid': _("This value must contain only letters, "
                         "numbers and underscores."),
        }
    )

    def __init__(self, *args, **kwargs):
        questions = kwargs.pop("questions", [])
        super(ForgotPasswordForm, self).__init__(*args, **kwargs)

        for index, question in enumerate(questions):
            self.fields["question_%s" % index] = forms.CharField(
                label=question.title,
                widget=forms.TextInput(
                    attrs=dict(
                        required=True,
                        max_length=150,
                    )
                )
            )


class ResetPasswordForm(forms.Form):
    username = forms.CharField(
        widget=forms.HiddenInput()
    )

    token = forms.CharField(
        widget=forms.HiddenInput()
    )

    password = forms.RegexField(
        regex=r'^\d{4}$',
        widget=forms.PasswordInput(
            attrs=dict(
                required=True,
                render_value=False,
                type='password',
            )
        ),
        max_length=4,
        min_length=4,
        error_messages={
            'invalid': _("This value must contain only numbers."),
        },
        label=_("PIN")
    )

    confirm_password = forms.RegexField(
        regex=r'^\d{4}$',
        widget=forms.PasswordInput(
            attrs=dict(
                required=True,
                render_value=False,
                type='password',
            )
        ),
        max_length=4,
        min_length=4,
        error_messages={
            'invalid': _("This value must contain only numbers."),
        },
        label=_("Confirm PIN")
    )
