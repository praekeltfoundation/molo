from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login, logout
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.http.request import QueryDict
from django.http.response import HttpResponseForbidden
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from molo.core.templatetags.core_tags import get_pages
from molo.profiles import forms
from molo.profiles.models import SecurityAnswer, SecurityQuestion
from molo.profiles.models import UserProfile, UserProfilesSettings


class RegistrationView(FormView):
    """
    Handles user registration
    """
    form_class = forms.RegistrationForm
    template_name = "profiles/register.html"

    def form_valid(self, form):
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        alias = form.cleaned_data["alias"]
        date_of_birth = form.cleaned_data["date_of_birth"]
        gender = form.cleaned_data["gender"]
        location = form.cleaned_data["location"]
        education_level = form.cleaned_data["education_level"]
        mobile_number = form.cleaned_data["mobile_number"]
        try:
            user = User.objects.create_user(
                username=username, password=password)
        except:
            messages.error(
                self.request,
                _('Username is already taken')
            )
            return render(self.request, self.template_name,
                          {'form': form})
        user.profile.mobile_number = mobile_number
        user.profile.alias = alias
        user.profile.date_of_birth = date_of_birth
        user.profile.gender = gender
        user.profile.location = location
        user.profile.education_level = education_level
        user.profile.site = self.request._wagtail_site
        if form.cleaned_data["email"]:
            user.email = form.cleaned_data["email"]
            user.save()
        user.profile.save()

        for index, question in enumerate(self.questions):
            answer = form.cleaned_data.get("question_%s" % index)
            if answer:
                SecurityAnswer.objects.create(
                    user=user.profile,
                    question=question,
                    answer=answer
                )
        authed_user = authenticate(
            request=self.request, username=username, password=password)
        login(self.request, authed_user)
        return HttpResponseRedirect(form.cleaned_data.get("next", "/"))

    def get_form_kwargs(self):
        kwargs = super(RegistrationView, self).get_form_kwargs()
        self.questions = SecurityQuestion.objects.descendant_of(
            self.request._wagtail_site.root_page).live().filter(
            language__is_main_language=True)

        context = {"request": self.request}
        self.translated_questions = get_pages(
            context, self.questions, self.request.LANGUAGE_CODE)
        kwargs["questions"] = self.translated_questions
        kwargs["request"] = self.request
        return kwargs


class RegistrationDone(LoginRequiredMixin, FormView):
    form_class = forms.DoneForm
    template_name = 'profiles/done.html'

    def form_valid(self, form):
        profile = self.request.user.profile
        site = self.request._wagtail_site
        if (UserProfilesSettings.for_site(
            site).activate_dob) and not (
            UserProfilesSettings.for_site(
                site).capture_dob_on_reg):
            profile.date_of_birth = form.cleaned_data["date_of_birth"]
        if (UserProfilesSettings.for_site(
            site).activate_display_name) and not (
            UserProfilesSettings.for_site(
                site).capture_display_name_on_reg):
            profile.alias = form.cleaned_data["alias"]
        if (UserProfilesSettings.for_site(
            site).activate_gender) and not (
            UserProfilesSettings.for_site(
                site).capture_gender_on_reg):
            profile.gender = form.cleaned_data["gender"]
        if (UserProfilesSettings.for_site(
            site).activate_location) and not (
            UserProfilesSettings.for_site(
                site).capture_location_on_reg):
            profile.location = form.cleaned_data["location"]
        if (UserProfilesSettings.for_site(
            site).activate_education_level) and not (
            UserProfilesSettings.for_site(
                site).capture_education_level_on_reg):
            profile.education_level = form.cleaned_data["education_level"]
        profile.save()
        return HttpResponseRedirect(form.cleaned_data.get('next', '/'))

    def get_form_kwargs(self):
        kwargs = super(RegistrationDone, self).get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


def logout_page(request):
    logout(request)
    return HttpResponseRedirect(request.GET.get('next', '/'))


class MyProfileView(LoginRequiredMixin, TemplateView):
    """
    Enables viewing of the user's profile in the HTML site, by the profile
    owner.
    """
    template_name = 'profiles/viewprofile.html'

    def get_context_data(self, **kwargs):
        context = super(MyProfileView, self).get_context_data(**kwargs)
        context['password_change_form'] = forms.ProfilePasswordChangeForm()
        return context


class MyProfileEdit(LoginRequiredMixin, UpdateView):
    """
    Enables editing of the user's profile in the HTML site
    """
    model = UserProfile
    form_class = forms.EditProfileForm
    template_name = 'profiles/editprofile.html'
    success_url = reverse_lazy('molo.profiles:view_my_profile')

    def get_initial(self):
        initial = super(MyProfileEdit, self).get_initial()
        initial.update({'email': self.request.user.email})
        return initial

    def form_valid(self, form):
        super(MyProfileEdit, self).form_valid(form)
        self.request.user.email = form.cleaned_data['email']
        self.request.user.save()
        return HttpResponseRedirect(
            reverse('molo.profiles:view_my_profile'))

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_form_kwargs(self):
        kwargs = super(MyProfileEdit, self).get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


class ProfilePasswordChangeView(LoginRequiredMixin, FormView):
    form_class = forms.ProfilePasswordChangeForm
    template_name = 'profiles/change_password.html'

    def form_valid(self, form):
        user = self.request.user
        if user.check_password(form.cleaned_data['old_password']):
            user.set_password(form.cleaned_data['new_password'])
            user.save()
            return HttpResponseRedirect(
                reverse('molo.profiles:view_my_profile'))
        messages.error(
            self.request,
            _('The old password is incorrect.')
        )
        return render(self.request, self.template_name,
                      {'form': form})


class ForgotPasswordView(FormView):
    form_class = forms.ForgotPasswordForm
    template_name = "profiles/forgot_password.html"

    def form_valid(self, form):
        error_message = "The username and security question(s) combination " \
                        + "do not match."
        profile_settings = UserProfilesSettings.for_site(
            self.request._wagtail_site)

        if "forgot_password_attempts" not in self.request.session:
            self.request.session["forgot_password_attempts"] = \
                profile_settings.password_recovery_retries

        # max retries exceeded
        if self.request.session["forgot_password_attempts"] <= 0:
            form.add_error(
                None,
                _("Too many attempts. Please try again later.")
            )
            return self.render_to_response({'form': form})
        site = self.request._wagtail_site
        username = form.cleaned_data["username"]
        try:
            user = User.objects.get(
                profile__migrated_username=username,
                profile__site=site)
            username = user.username
        except User.DoesNotExist:
            try:
                user = User.objects.get(
                    username=username, profile__site=site)
            except User.DoesNotExist:
                self.request.session['forgot_password_attempts'] += 1
                form.add_error('username',
                               _('The username that you entered appears to be '
                                 'invalid. Please try again.'))
                return self.render_to_response({'form': form})

        if not user.is_active:
            # add non_field_error
            form.add_error(None, _(error_message))
            self.request.session["forgot_password_attempts"] -= 1
            return self.render_to_response({'form': form})

        # check security question answers
        answer_checks = []
        for i in range(profile_settings.num_security_questions):
            user_answer = form.cleaned_data.get("question_%s" % (i,))
            try:
                saved_answer = user.profile.securityanswer_set.get(
                    user=user.profile,
                    question=self.security_questions[i]
                )
                answer_checks.append(saved_answer.check_answer(user_answer))
            except SecurityAnswer.DoesNotExist:
                form.add_error(
                    None,
                    _("There are no security questions "
                      "stored against your profile."))
                return self.render_to_response({'form': form})

        # redirect to reset password page if username and security
        # questions were matched
        if all(answer_checks):
            token = default_token_generator.make_token(user)
            q = QueryDict(mutable=True)
            q["user"] = username
            q["token"] = token
            reset_password_url = "{0}?{1}".format(
                reverse("molo.profiles:reset_password"), q.urlencode()
            )
            return HttpResponseRedirect(reset_password_url)
        else:
            form.add_error(None, _(error_message))
            self.request.session["forgot_password_attempts"] -= 1
            return self.render_to_response({'form': form})

    def get_form_kwargs(self):
        # add security questions for form field generation
        # the security questions should be a random subset of
        # all the questions the user has answered
        site = self.request._wagtail_site
        kwargs = super(ForgotPasswordView, self).get_form_kwargs()
        profile_settings = UserProfilesSettings.for_site(site)
        self.security_questions = SecurityQuestion.objects.descendant_of(
            site.root_page).live().filter(
            language__is_main_language=True
        )

        context = {"request": self.request}
        translated_questions = get_pages(
            context, self.security_questions, self.request.LANGUAGE_CODE
        )
        kwargs["questions"] = translated_questions[
            :profile_settings.num_security_questions]
        # limit security questions - done here because query in get_pages()
        # cannot be performed once queryset is sliced into a list
        self.security_questions = self.security_questions[
            :profile_settings.num_security_questions]
        return kwargs


class ResetPasswordView(FormView):
    form_class = forms.ResetPasswordForm
    template_name = "profiles/reset_password.html"

    def form_valid(self, form):
        username = form.cleaned_data["username"]
        token = form.cleaned_data["token"]

        try:
            user = User.objects.get_by_natural_key(username)
        except User.DoesNotExist:
            return HttpResponseForbidden()

        if not user.is_active:
            return HttpResponseForbidden()

        if not default_token_generator.check_token(user, token):
            return HttpResponseForbidden()

        password = form.cleaned_data["password"]
        confirm_password = form.cleaned_data["confirm_password"]

        if password != confirm_password:
            form.add_error(None,
                           _("The two PINs that you entered do not match. "
                             "Please try again."))
            return self.render_to_response({"form": form})

        user.set_password(password)
        user.save()
        self.request.session.flush()

        return HttpResponseRedirect(
            reverse("molo.profiles:reset_password_success")
        )

    def render_to_response(self, context, **response_kwargs):
        username = self.request.GET.get("user")
        token = self.request.GET.get("token")

        if not username or not token:
            return HttpResponseForbidden()

        context["form"].initial.update({
            "username": username,
            "token": token
        })

        return super(ResetPasswordView, self).render_to_response(
            context, **response_kwargs
        )
