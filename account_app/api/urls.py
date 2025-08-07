from django.urls import path
from account_app.api import views

urlpatterns = [
    # Role selection (booker or scheduler)
    path('role/', views.RoleSelectionView.as_view(), name='select-role'),

    # Booker registration via phone number with OTP
    path('register-phone/booker/', views.RegisterBookerWithPhoneView.as_view(), name='otp-register-booker'),

    # Scheduler registration via phone number with OTP
    path('register-phone/scheduler/', views.RegisterSchedulerWithPhoneView.as_view(), name='otp-register-scheduler'),

    # Verify OTP code after registration or login
    path('verify/', views.VerifyOTPView.as_view(), name='verify-otp'),

    # Login with phone number (OTP will be sent)
    path('login/', views.OTPLoginView.as_view(), name='otp-login'),

    # Verify OTP for login and generate access/refresh tokens
    path('login/verify/', views.OTPLoginVerifyView.as_view(), name='otp-login-verify'),

    # Logout and blacklist refresh token to prevent reuse
    path('logout/', views.LogoutAndBlacklistRefreshTokenForUserView.as_view(), name='logout'),
]
