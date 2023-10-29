from django.urls import path
from . import views
from .views import CustomPasswordResetView,CustomPasswordResetDoneView,CustomPasswordResetConfirmView,CustomPasswordResetCompleteView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('tenantpage/', views.tenant, name='tenantpage'),
    path('ownerpage/', views.owner, name='ownerpage'),
    path('ownerpg/',views.ownerpg,name='ownerpg'),
    path('tenantpg/',views.tenantpg,name='tenantpg'),
    path('manageprop/',views.manageprop,name='manageprop'),

    path('adminhome/', views.adminh, name='adminhome'),
    path('adminregusers/', views.adminreg, name='adminregusers'),
    path('deactivate_user/<int:user_id>/', views.deactivate_user, name='deactivate_user'),
    path('activate_user/<int:user_id>/', views.activate_user, name='activate_user'),


    path('activate/<uidb64>/<token>',views.ActivateAccountView.as_view(),name='activate'),
    # Password Reset Views
     path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
     path('password_reset/done/',CustomPasswordResetDoneView.as_view(),name='password_reset_done'),
     path('reset/<uidb64>/<token>/',CustomPasswordResetConfirmView.as_view(),name='password_reset_confirm'),
     path('reset/done/',CustomPasswordResetCompleteView.as_view(),name='password_reset_complete'),

     

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


