from django.db.models import F
from django.shortcuts import get_object_or_404, render

from .models import Blog


def blog_list(request):
    blogs = Blog.objects.all()
    return render(request, 'blog/blog_list.html', {'blogs': blogs})


def blog_detail(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    Blog.objects.filter(pk=blog.pk).update(likes=F('likes') + 1)
    blog.refresh_from_db()
    return render(request, 'blog/blog_detail.html', {'blog': blog})
