from django.views import generic
# from django.utils import timezone
from .models import MarkdownPost
import logging

log = logging.getLogger("blog.views")


class PostList(generic.ListView):
    model = MarkdownPost
    # today = timezone.now()
    queryset = MarkdownPost.objects.live().order_by('-modified_date')
    template_name = 'docrootcms_blog/index.html'


class PostDetail(generic.DetailView):
    model = MarkdownPost
    template_name = 'docrootcms_blog/post_detail.html'
