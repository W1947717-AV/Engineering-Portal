from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views
from dashboard_app import views as dashboard_views

urlpatterns = [
    path('', lambda request: redirect('/dashboard/')),

    path('login/', auth_views.LoginView.as_view(
        template_name='login.html'
    ), name='login'),

    path('logout/', auth_views.LogoutView.as_view(
        template_name='logout.html'
    ), name='logout'),

    path('register/', dashboard_views.register, name='register'),

    # Password reset flow
    path('forgot-password/', auth_views.PasswordResetView.as_view(
        template_name='forgot_password.html',
        email_template_name='password_reset_email.html',
        subject_template_name='password_reset_subject.txt',
        success_url='/forgot-password/done/'
    ), name='password_reset'),

    path('forgot-password/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='forgot_password_done.html'
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='password_reset_confirm.html',
        success_url='/reset/done/'
    ), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='password_reset_complete.html'
    ), name='password_reset_complete'),

    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard_app.urls')),
    path('teams/', include('teams.urls')),
    path('messages/', include('messages_app.urls')),
    path('schedule/', include('schedule_app.urls')),
    path('profile/', dashboard_views.profile_update, name='profile'),
    path('change-password/', dashboard_views.change_password, name='change_password'),
]