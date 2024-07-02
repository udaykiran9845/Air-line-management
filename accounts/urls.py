
from django.urls import path,include
from . import views
import django.contrib.auth.urls
from django_email_verification import urls as mail_urls
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register',views.register,name="register"),
    path('login',views.login,name="login"),
    path('logout',views.logout,name="logout"),
    path('email/',include(mail_urls)),
    path('reset_password/',auth_views.PasswordResetView.as_view(template_name ="password_reset.html"),name="reset_passsword"),
    path('reset_passsword_sent/',auth_views.PasswordResetDoneView.as_view(template_name ="password_reset_sent.html"),name="password_reset_done"),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name ="password_reset_form.html"),name="password_reset_confirm"),
    path('reset_passsword_complete/',auth_views.PasswordResetCompleteView.as_view(template_name ="password_reset_done.html"),name="password_reset_complete"),
]
