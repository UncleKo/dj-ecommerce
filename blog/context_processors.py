#### Settings.pyに'blog.context_processors.global_val'を追加 ###

from .models import Category, Tag, Post
from django.db.models import Count


def global_val(request):
    archives = Post.objects.filter(draft=False).values(
        'date_posted__year', 'date_posted__month').annotate(Count('id')).order_by()

    return {
        'latest_posts': Post.objects.filter(draft=False).order_by('-date_posted')[:5],
        'drafts': Post.objects.filter(draft=True).order_by('-date_posted'),
        # 'categories': Category.objects.all(),
        'post_categories': Category.objects.annotate(num_posts=Count('posts')).order_by('-num_posts'),
        # 'tags': Tag.objects.all(),
        'post_tags': Tag.objects.annotate(num_posts=Count('posts')).order_by('-num_posts'),
        'archives': archives
    }
