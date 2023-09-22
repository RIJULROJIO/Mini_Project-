from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup.html', views.signup, name='signup'),
    path('login.html', views.login, name='login'),


   


]
