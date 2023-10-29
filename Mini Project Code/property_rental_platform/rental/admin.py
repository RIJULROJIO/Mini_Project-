from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser,UserProfile,Profile,Property



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
    list_display = ( 'property_type', 'address', 'bedrooms', 'bathrooms', 'monthly_rent', 'security_deposit', 'lease_duration', 'availability_date', 'furnished')
    list_filter = ('property_type', 'lease_duration', 'furnished')
   
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Property, PropertyAdmin)



