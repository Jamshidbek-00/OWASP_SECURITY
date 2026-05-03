from django.contrib import admin

# Register your models here.
from .models import SiteUser, Note

admin.site.register(SiteUser)
admin.site.register(Note)