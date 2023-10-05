from django.urls import path
from . import views
from .views import CustomPasswordResetView,CustomPasswordResetDoneView,CustomPasswordResetConfirmView,CustomPasswordResetCompleteView

from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('tenantpage/', views.tenant, name='tenantpage'),
    
    # Password Reset Views
     path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
     path('password_reset/done/',CustomPasswordResetDoneView.as_view(),name='password_reset_done'),
     path('reset/<uidb64>/<token>/',CustomPasswordResetConfirmView.as_view(),name='password_reset_confirm'),
     path('reset/done/',CustomPasswordResetCompleteView.as_view(),name='password_reset_complete'),
]

