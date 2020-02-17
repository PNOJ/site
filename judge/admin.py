from django.contrib import admin, auth
from django.contrib.auth import get_user_model
from . import models

User = get_user_model()

# Register your models here.

# class PNOJAdminSite(admin.AdminSite):
#     site_header = "PNOJ administration"
#     site_title = "PNOJ admin"

# admin_site = PNOJAdminSite()

class ProblemAdmin(admin.ModelAdmin):
    fields = ('problem_file', 'slug')


admin.site.register(User)
admin.site.register(models.SidebarItem)
admin.site.register(models.Problem, ProblemAdmin)
admin.site.register(models.Submission)
admin.site.register(models.ProblemCategory)
admin.site.register(models.ProblemType)
admin.site.register(models.Organization)
admin.site.register(models.Comment)
admin.site.site_header = "PNOJ administration"
admin.site.site_title = "PNOJ admin"
# admin_site.register(auth.models.Group)
