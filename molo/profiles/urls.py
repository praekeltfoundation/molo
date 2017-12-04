from molo.profiles import views
from molo.profiles.forms import MoloAuthenticationForm

from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView


urlpatterns = [
    url(r'^logout/$', views.logout_page, name='auth_logout'),
    # If user is not login it will redirect to login page
    url(r'^login/$', auth_views.login,
        {'authentication_form': MoloAuthenticationForm}, name='auth_login'),
    url(
        r'^register/$',
        views.RegistrationView.as_view(),
        name='user_register'),
    url(
        r'^register/done/',
        login_required(views.RegistrationDone.as_view(
            template_name="profiles/done.html"
        )),
        name='registration_done'
    ),
    url(
        r'^view/myprofile/$',
        login_required(views.MyProfileView.as_view()),
        name='view_my_profile'
    ),
    url(
        r'^edit/myprofile/$',
        login_required(views.MyProfileEdit.as_view()),
        name='edit_my_profile'
    ),
    url(
        r'^password-reset/$',
        login_required(views.ProfilePasswordChangeView.as_view()),
        name="profile_password_change"
    ),
    url(
        r"^forgot-password/$",
        views.ForgotPasswordView.as_view(),
        name="forgot_password"
    ),
    url(
        r"^reset-password/$",
        views.ResetPasswordView.as_view(),
        name="reset_password"
    ),
    url(
        r"^reset-success/$",
        TemplateView.as_view(
            template_name="profiles/reset_password_success.html"
        ),
        name="reset_password_success"
    ),
    url(
        r"^login-success/$",
        TemplateView.as_view(
            template_name="profiles/login_success.html"
        ),
        name="login_success"
    ),
]
