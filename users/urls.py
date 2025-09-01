from django.urls import path, include
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from allauth.account.views import LoginView, SignupView, LogoutView
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication URLs (using allauth)
    path('accounts/', include('allauth.urls')),

    # Custom provider signup
    path('signup/provider/', views.ProviderSignUpView.as_view(), name='provider_signup'),

    # Password Reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='users/password_reset.html',
        email_template_name='users/password_reset_email.html',
        subject_template_name='users/password_reset_subject.txt'
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='users/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='users/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='users/password_reset_complete.html'
    ), name='password_reset_complete'),

    # Profile URLs
    path('profile/', login_required(views.ProfileView.as_view()), name='profile'),
    path('profile/edit/', login_required(views.ProfileUpdateView.as_view()), name='profile_edit'),

    # Provider URLs
    path('provider/<str:username>/', views.ProviderDetailView.as_view(), name='provider_detail'),
    path('profile/change-password/', login_required(views.PasswordChangeView.as_view(
        template_name='users/password_change.html'
    )), name='change_password'),
    path('profile/addresses/', login_required(views.AddressListView.as_view()), name='address_list'),
    path('profile/addresses/add/', login_required(views.AddressCreateView.as_view()), name='address_add'),
    path('profile/addresses/<int:pk>/edit/', login_required(views.AddressUpdateView.as_view()), name='address_edit'),
    path('profile/addresses/<int:pk>/delete/', login_required(views.AddressDeleteView.as_view()), name='address_delete'),
    path('profile/notifications/', login_required(views.NotificationListView.as_view()), name='notification_list'),
    path('profile/notifications/<int:pk>/', login_required(views.NotificationDetailView.as_view()), name='notification_detail'),
    path('profile/notifications/mark-all-read/', login_required(views.mark_all_notifications_read), name='mark_all_notifications_read'),

    # Provider Dashboard URLs
    path('dashboard/', login_required(views.ProviderDashboardView.as_view()), name='provider_dashboard'),
    path('dashboard/services/', login_required(views.ProviderServiceListView.as_view()), name='provider_service_list'),
    path('dashboard/services/add/', login_required(views.ProviderServiceCreateView.as_view()), name='provider_service_add'),
    path('dashboard/services/<int:pk>/edit/', login_required(views.ProviderServiceUpdateView.as_view()), name='provider_service_edit'),
    path('dashboard/services/<int:pk>/delete/', login_required(views.ProviderServiceDeleteView.as_view()), name='provider_service_delete'),
    path('dashboard/bookings/', login_required(views.ProviderBookingListView.as_view()), name='provider_booking_list'),
    path('dashboard/bookings/<int:pk>/', login_required(views.ProviderBookingDetailView.as_view()), name='provider_booking_detail'),
    path('dashboard/bookings/<int:pk>/update-status/', login_required(views.update_booking_status), name='provider_booking_update_status'),
    path('dashboard/schedule/', login_required(views.ProviderScheduleView.as_view()), name='provider_schedule'),
    path('dashboard/reviews/', login_required(views.ProviderReviewListView.as_view()), name='provider_review_list'),
    path('dashboard/profile/', login_required(views.ProviderProfileView.as_view()), name='provider_profile'),
    path('dashboard/profile/edit/', login_required(views.ProviderProfileUpdateView.as_view()), name='provider_profile_edit'),
]
