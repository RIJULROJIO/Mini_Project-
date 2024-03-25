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
        path('propsellimgup/<int:property_id>/', views.propsellimgup, name='propsellimgup'),

    
    path('propdocs/<int:property_id>/', views.propdocs, name='propdocs'),
    path('submit_rental_request/<int:property_id>/', views.submit_rental_request, name='submit_rental_request'),

    path('admprop/',views.admprop,name='admprop'),
        path('admviewdocs/<int:property_id>/', views.admviewdocs, name='admviewdocs'),
        path('accept_rental_request/<int:request_id>/', views.accept_rental_request, name='accept_rental_request'),
        path('lease/<int:property_id>/', views.lease, name='lease'),
        # path('viewlease/<int:lease_agreement_id>/', views.view_lease_agreement, name='viewlease'),


        path('handle_payment/', views.handle_payment, name='handle_payment'),
        path('handle_pay/', views.handle_pay, name='handle_pay'),


    path('payment/<int:property_id>/', views.rentnxt, name='payment'),
    path('paymentnxt/<int:property_id>/', views.rentnxtt, name='paymentnxt'),
    path('payservice/<int:service_id>/', views.serpay, name='payservice'),


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


    path('serproviderpage/', views.serproviderpage, name='serproviderpage'),
    path('adminserpropage/', views.adminserpropage, name='adminserpropage'),
    path('serproviderdash/',views.serproviderdash,name='serproviderdash'),
    path('edit-service/<int:service_id>/', views.edit_service, name='edit_service'),
        path('delete_service/<int:service_id>/', views.delete_service, name='delete_service'),


    path('admin-approve-profile/<int:profile_id>/', views.approve_profile, name='approve_profile'),
    path('admin-reject-profile/<int:profile_id>/', views.reject_profile, name='reject_profile'),

    path('clear_rental_requests/<int:property_id>/', views.clear_rental_requests, name='clear_rental_requests'),
    path('view_locations/',views.view_locations,name='view_locations'),

    path('adminpay', views.admin_dashboard, name='adminpay'),

    path('rentcollect/', views.rent_collection, name='rentcollect'),

    path('propertyfeedback/<int:property_id>/', views.property_feedback, name='propertyfeedback'),

    path('services/<str:property_type>/', views.view_services, name='services'),
    path('request_service/<int:service_id>/', views.request_service, name='request_service'),
    path('schedule-service/<int:request_id>/', views.schedule_service, name='schedule_service'),
    path('mark_as_done/<int:request_id>/', views.mark_as_done, name='mark_as_done'),

    


        path('upload-profile-picture/', views.upload_profile_picture, name='upload_profile_picture'),
            path('check-face-detection/', views.check_face_detection, name='check_face_detection'),


        path('ad_click/', views.ad_click, name='ad_click'),
        path('financecentre/', views.finance, name='financecentre'),
        path('sellproperty/', views.sellprop, name='sellproperty'),
            path('my-properties/', views.view_properties, name='view_properties'),
                        path('buyprop/', views.view_property, name='buyprop'),


                         path('inbox/', views.inbox, name='inbox'),
    path('compose/', views.compose_message, name='compose_message'),
    path('mark_as_read/<int:message_id>/', views.mark_as_read, name='mark_as_read'),
    path('delete_message/<int:message_id>/', views.delete_message, name='delete_message'),

        path('verify_property/<int:property_id>/', views.verify_property, name='verify_property'),

            path('validate-username/', views.validate_username, name='validate_username'),  # Add this line











    


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


