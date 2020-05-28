from django.contrib import admin

from .models import CustomUser, Profile, Code

admin.site.register(CustomUser)
admin.site.register(Profile)
admin.site.register(Code)
# Register your models here.
