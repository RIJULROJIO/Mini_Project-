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
    path('propimgup/<int:property_id>/', views.propimgup, name='propimgup'),
    path('propdocs/<int:property_id>/', views.propdocs, name='propdocs'),
    path('submit_rental_request/<int:property_id>/', views.submit_rental_request, name='submit_rental_request'),

    path('admprop/',views.admprop,name='admprop'),
        path('admviewdocs/<int:property_id>/', views.admviewdocs, name='admviewdocs'),
        path('accept_rental_request/<int:request_id>/', views.accept_rental_request, name='accept_rental_request'),
        path('lease/<int:property_id>/', views.lease, name='lease'),
        # path('viewlease/<int:lease_agreement_id>/', views.view_lease_agreement, name='viewlease'),



        path('payment/', views.rentnxt, name='payment'),
    path('generate_property_pdf/<int:property_id>/', views.generate_property_pdf, name='generate_property_pdf'),
    path('notifications/', views.view_notifications, name='view_notifications'),
    path('notifications/mark_as_read/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),


    path('propamenity/<int:property_id>/', views.propamenity, name='propamenity'),
        path('property/<int:property_id>/', views.property_detail, name='property_detail'),
        path('ownerinfo/<int:property_id>/', views.ownerinfo, name='ownerinfo'),
        path('update_property/<int:property_id>/', views.update_property_view, name='update_property'),

            # path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
            #  path('cart/', views.view_cart, name='view_cart'),
                #path('submit_rental_request/', views.submit_rental_request, name='submit_rental_request'),






    path('adminhome/', views.adminh, name='adminhome'),
    path('adminregusers/', views.adminreg, name='adminregusers'),
        path('property_images/<int:property_id>/', views.property_images, name='property_images'),

    path('deactivate_user/<int:user_id>/', views.deactivate_user, name='deactivate_user'),
    path('activate_user/<int:user_id>/', views.activate_user, name='activate_user'),


    path('activate/<uidb64>/<token>',views.ActivateAccountView.as_view(),name='activate'),
     path('approve_property/<int:property_id>/', views.approve_property, name='approve_property'),
    path('reject_property/<int:property_id>/', views.reject_property, name='reject_property'),
  
    # Password Reset Views
     path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
     path('password_reset/done/',CustomPasswordResetDoneView.as_view(),name='password_reset_done'),
     path('reset/<uidb64>/<token>/',CustomPasswordResetConfirmView.as_view(),name='password_reset_confirm'),
     path('reset/done/',CustomPasswordResetCompleteView.as_view(),name='password_reset_complete'),

     

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


