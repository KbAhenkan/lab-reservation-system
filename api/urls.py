from django.urls import path, include
from . import views

urlpatterns = [
    # AUTH URLS
    path('auth/signup/', views.signup, name='signup'),
    path('auth/login/', views.login, name='login'),
    path('auth/password-reset/', views.password_reset_request, name='password_reset_request'),
    path('auth/password-reset/confirm/', views.password_reset_confirm, name='password_reset_confirm'),

    # DASHBOARD URLS
    path('dashboard/', views.dashboard, name='dashboard'),

    # USER URLS
    path('users/', views.user_list, name='user_list'),
    path('users/<int:pk>/', views.user_detail, name='user_detail'),
    
    #LAB URLS
    path('labs/', views.lab_list, name='lab_list'),
    path('labs/<int:pk>/', views.lab_detail, name='lab_detail'),

    # Reservation URLS
    path('reservations/', views.reservation_list, name='reservation_list'),
    path('reservations/<int:pk>/', views.reservation_detail, name='reservation_detail'),

]
