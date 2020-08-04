from django.contrib import admin, auth
from django.contrib.auth import get_user_model
from . import models
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

User = get_user_model()

# Register your models here.

class ProblemAdmin(admin.ModelAdmin):
    fields = ['problem_file', 'slug']

    def has_view_permission(self, request, obj=None):
        if request.user.has_perm('judge.view_problem'):
            if obj == None:
                return True
            else:
                return request.user in obj.author.all()
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.has_perm('judge.change_problem'):
            if obj == None:
                return True
            else:
                return request.user in obj.author.all()
        return False

    def has_module_permission(self, request):
        perms = ['judge.add_problem', 'judge.view_problem', 'judge.change_problem', 'judge.delete_problem']
        return True in [request.user.has_perm(i) for i in perms]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)

class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'owner', 'member_count', 'is_open']

    def has_view_permission(self, request, obj=None):
        if request.user.has_perm('judge.view_organization'):
            if obj == None:
                return True
            else:
                return request.user in obj.admins.all() or request.user == obj.owner
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.has_perm('judge.change_organization'):
            if obj == None:
                return True
            else:
                return request.user == obj.owner
        return False

    def has_module_permission(self, request):
        perms = ['judge.add_organization', 'judge.view_organization', 'judge.change_organization', 'judge.delete_organization']
        # num_affiliated_organizations = request.user.organizations_owning.all().count() + request.user.organizations_maintaining.all().count()
        # return True in [request.user.has_perm(i) for i in perms] or num_affiliated_organizations > 0
        return True in [request.user.has_perm(i) for i in perms]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(Q(admins=request.user) | Q(owner=request.user))

class OrganizationRequestAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'user', 'organization', 'created', 'status', 'reviewed']
    list_filter = ['organization', 'status']

    def has_given_permission(self, request, obj, permission):
        if request.user.has_perm(permission):
            if obj == None:
                return True
            else:
                return request.user in obj.organization.admins.all()
        return False

    def has_view_permission(self, request, obj=None):
        return self.has_given_permission(request, obj, 'judge.view_organizationrequest')

    def has_change_permission(self, request, obj=None):
        return self.has_given_permission(request, obj, 'judge.change_organizationrequest')

    def has_module_permission(self, request):
        perms = ['judge.add_organizationrequest', 'judge.view_organizationrequest', 'judge.change_organizationrequest', 'judge.delete_organizationrequest']
        return True in [request.user.has_perm(i) for i in perms]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(organization__admins=request.user)

admin.site.register(User)
admin.site.register(models.SidebarItem)
admin.site.register(models.Problem, ProblemAdmin)
admin.site.register(models.Submission)
admin.site.register(models.ProblemCategory)
admin.site.register(models.ProblemType)
admin.site.register(models.Organization, OrganizationAdmin)
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
