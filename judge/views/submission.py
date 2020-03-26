from django.views.generic import DetailView, ListView
from .. import models
from django.views.generic.base import RedirectView
from django.contrib.contenttypes.models import ContentType

class SubmissionIndex(ListView):
    model = models.Submission
    context_object_name = 'submissions'
    template_name = 'judge/submission_list.html'
    paginate_by = 50

    def get_ordering(self):
        return '-created'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sidebar_items'] = models.SidebarItem.objects.order_by('order')
        context['page_title'] = 'PNOJ: Submissions'
        return context



class Submission(DetailView):
    model = models.Submission
    context_object_name = 'submission'
    template_name = 'judge/submission.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sidebar_items'] = models.SidebarItem.objects.order_by('order')
        context['page_title'] = 'PNOJ: Submission #' + str(self.get_object().pk)
        submission_contenttype = ContentType.objects.get_for_model(models.Submission)
        context['comments'] = models.Comment.objects.filter(parent_content_type=submission_contenttype, parent_object_id=self.get_object().pk)
        return context
