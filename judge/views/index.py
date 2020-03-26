from django.views.generic import DetailView, ListView
import judge.models as models
from django.contrib.contenttypes.models import ContentType

class Index(ListView):
    template_name = 'judge/index.html'
    model = models.BlogPost
    context_object_name = 'posts'

    def get_ordering(self):
        return '-created'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sidebar_items'] = models.SidebarItem.objects.order_by('order')
        context['page_title'] = 'PNOJ'
        return context

class BlogPost(DetailView):
    model = models.BlogPost
    context_object_name = 'post'
    template_name = "judge/blog_post.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sidebar_items'] = models.SidebarItem.objects.order_by('order')
        context['page_title'] = 'PNOJ: ' + self.get_object().title
        blogpost_contenttype = ContentType.objects.get_for_model(models.BlogPost)
        context['comments'] = models.Comment.objects.filter(parent_content_type=blogpost_contenttype, parent_object_id=self.get_object().pk)
        return context
