from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser,UserProfile,Profile,Property,RentalRequest,Payment,ServiceRequest,ScheduledService



class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email', 'role')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'role', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )

    def get_queryset(self, request):
        # Exclude superusers from the admin table
        return CustomUser.objects.exclude(is_superuser=True)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'date_of_birth', 'gender', 'phone_number', 'current_address', 'photo_id')

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'date_of_birth', 'gender', 'phone_number', 'current_address', 'photo_id')
    
class PropertyAdmin(admin.ModelAdmin):
    list_display = ( 'property_type', 'address', 'monthly_rent', 'security_deposit', 'lease_duration', 'availability_date',)
    list_filter = ('property_type', 'lease_duration')
   
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Property, PropertyAdmin)


@admin.register(RentalRequest)
class RentalRequestAdmin(admin.ModelAdmin):
    list_display = ['property', 'tenant', 'created_at', 'status']
    list_filter = ['status']
    search_fields = ['property__property_type', 'tenant__full_name']  # Adjust as needed



class PaymentAdmin(admin.ModelAdmin):
    list_display = ('razorpay_payment_id', 'razorpay_order_id', 'property', 'user_profile', 'amount', 'timestamp')
    list_filter = ('property', 'user_profile', 'timestamp')
    search_fields = ('razorpay_payment_id', 'user_profile__user__username', 'property__address')
    readonly_fields = ('timestamp',)

admin.site.register(Payment, PaymentAdmin)

class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('service', 'user', 'message', 'timestamp')
    search_fields = ('service__service_name', 'user__full_name', 'message')
    list_filter = ('service__service_category', 'timestamp')

admin.site.register(ServiceRequest, ServiceRequestAdmin)

class ScheduledServiceAdmin(admin.ModelAdmin):
    list_display = ('service_request', 'scheduled_date', 'scheduled_time', 'is_done')
    list_filter = ('is_done', 'scheduled_date')
    search_fields = ('service_request__service__service_name', 'service_request__user__username')  # Assuming these are the related fields

admin.site.register(ScheduledService, ScheduledServiceAdmin)



from .models import Propertysell

@admin.register(Propertysell)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'property_type', 'address', 'sale_price')
    search_fields = ('user_profile__full_name', 'address', 'sale_price')
    list_filter = ('property_type', 'state', 'district', 'town')

from .models import LoanApplication

# @admin.register(LoanApplication)
# class LoanApplicationAdmin(admin.ModelAdmin):
#     list_display = ('applicant_name', 'property', 'loan_amount', 'occupation', 'email')
#     list_filter = ('occupation',)
#     search_fields = ('applicant_name', 'email', 'property__address')



from django.contrib import admin
from .models import Message

admin.site.register(Message)
