from molo.profiles import views
from molo.profiles.forms import MoloAuthenticationForm

from django.conf.urls import re_path
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView


urlpatterns = [
    re_path(r'^logout/$', views.logout_page, name='auth_logout'),
    # If user is not login it will redirect to login page
    re_path(
        r'^login/$',
        auth_views.LoginView.as_view(
            authentication_form=MoloAuthenticationForm),
        name='auth_login'),
    re_path(
        r'^register/$',
        views.RegistrationView.as_view(),
        name='user_register'),
    re_path(
        r'^register/done/',
        views.RegistrationDone.as_view(
            template_name="profiles/done.html"
        ),
        name='registration_done'
    ),
    re_path(
        r'^view/myprofile/$',
        views.MyProfileView.as_view(),
        name='view_my_profile'
    ),
    re_path(
        r'^edit/myprofile/$',
        views.MyProfileEdit.as_view(),
        name='edit_my_profile'
    ),
    re_path(
        r'^password-reset/$',
        views.ProfilePasswordChangeView.as_view(),
        name="profile_password_change"
    ),
    re_path(
        r"^forgot-password/$",
        views.ForgotPasswordView.as_view(),
        name="forgot_password"
    ),
    re_path(
        r"^reset-password/$",
        views.ResetPasswordView.as_view(),
        name="reset_password"
    ),
    re_path(
        r"^reset-success/$",
        TemplateView.as_view(
            template_name="profiles/reset_password_success.html"
        ),
        name="reset_password_success"
    ),
    re_path(
        r"^login-success/$",
        TemplateView.as_view(
            template_name="profiles/login_success.html"
        ),
        name="login_success"
    ),
]
