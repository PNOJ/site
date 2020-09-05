from .. import models
from django.views.generic.base import ContextMixin
from django.views.generic.list import MultipleObjectMixin

class TitleMixin(ContextMixin):
    title = ''

    def get_title(self):
        return self.title

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.get_title()
        return context

class SidebarMixin(ContextMixin):
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sidebar_items'] = models.SidebarItem.objects.order_by('order')
        return context
