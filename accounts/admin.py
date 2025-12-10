from django.contrib import admin
from .models import Profile
from django.contrib.auth.models import User

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'profile'

class UserAdmin(admin.ModelAdmin):
    inlines = (ProfileInline,)

# unregister/register default User admin to inject inline
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
admin.site.unregister(User)
admin.site.register(User, DjangoUserAdmin)
admin.site.register(Profile)
