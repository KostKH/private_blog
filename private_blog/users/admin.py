from django.contrib import admin
from django.contrib.auth.admin import Group

admin.site.unregister(Group)
