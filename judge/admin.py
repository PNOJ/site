from django.contrib import admin, auth
from django.contrib.auth import get_user_model
from . import models
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from django.utils.translation import gettext_lazy as _


User = get_user_model()

# Register your models here.

# class PNOJAdminSite(admin.AdminSite):
#     site_header = "PNOJ administration"
#     site_title = "PNOJ admin"

# admin_site = PNOJAdminSite()

class ProblemAdmin(admin.ModelAdmin):
    fields = ('problem_file', 'slug')

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj == None:
            return True
        return request.user in obj.author.all()

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj == None:
            return True
        return request.user in obj.author.all()

class OrganizationRequestAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'created', 'reviewed')
    list_filter = ['organization', 'status']

admin.site.register(User)
admin.site.register(models.SidebarItem)
admin.site.register(models.Problem, ProblemAdmin)
admin.site.register(models.Submission)
admin.site.register(models.ProblemCategory)
admin.site.register(models.ProblemType)
admin.site.register(models.Organization)
admin.site.register(models.OrganizationRequest, OrganizationRequestAdmin)
admin.site.register(models.Comment)
admin.site.register(models.BlogPost)
admin.site.site_header = "PNOJ administration"
admin.site.site_title = "PNOJ admin"
# admin_site.register(auth.models.Group)


# Define a new FlatPageAdmin
class FlatPageAdmin(FlatPageAdmin):
    fieldsets = (
        (None, {'fields': ('url', 'title', 'content', 'sites')}),
        (_('Advanced options'), {
            'classes': ('collapse',),
            'fields': (
                'enable_comments',
                'registration_required',
                'template_name',
            ),
        }),
    )

# Re-register FlatPageAdmin
admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)
