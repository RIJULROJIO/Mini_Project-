from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('index.html', views.index, name='index'),
    path('signup.html', views.signup, name='signup'),
    path('login.html', views.login, name='login'),
    path('tenantpage.html', views.tenantpage, name='tenantpage'),
    path('ownerpage.html', views.ownerpage, name='ownerpage'),



   


]
