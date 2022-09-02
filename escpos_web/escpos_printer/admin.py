from django.contrib import admin

# Register your models here.
from django.contrib.auth.models import User, Group


admin.site.unregister(User)
admin.site.unregister(Group)