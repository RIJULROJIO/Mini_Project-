from django.urls import path
from . import views
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.views import PasswordResetDoneView
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.views import PasswordResetCompleteView





urlpatterns = [
    path('', views.index, name='index'),

    path('index.html', views.index, name='index'),
    path('signup.html', views.signup, name='signup'),
    path('login.html', views.login_view, name='login'),
    path('tenantpage.html', views.tenantpage, name='tenantpage'),
    path('ownerpage.html', views.ownerpage, name='ownerpage'),
    path('logout/',views.logout_view, name='logout_view'),
    path('adminhome.html',views.adminhome, name='adminhome'),
    path('adminregusers.html',views.user_profile_list,name='adminregusers')
    




   


]
