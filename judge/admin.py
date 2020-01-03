from django.contrib import admin, auth
from django.contrib.auth import get_user_model

User = get_user_model()

# Register your models here.

# class PNOJAdminSite(admin.AdminSite):
#     site_header = "PNOJ administration"
#     site_title = "PNOJ admin"

# admin_site = PNOJAdminSite()

admin.site.register(User)
admin.site.site_header = "PNOJ administration"
admin.site.site_title = "PNOJ admin"
# admin_site.register(auth.models.Group)
