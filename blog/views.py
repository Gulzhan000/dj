from django.db.models import F
from django.shortcuts import get_object_or_404, render

from .models import Blog
from .forms import BlogForm
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods


def blog_list(request):
    blogs = Blog.objects.all()
    return render(request, 'blog/blog_list.html', {'blogs': blogs})


def blog_detail(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    Blog.objects.filter(pk=blog.pk).update(likes=F('likes') + 1)
    blog.refresh_from_db()
    return render(request, 'blog/blog_detail.html', {'blog': blog})


@require_http_methods(['GET', 'POST'])
def blog_create(request):
    form = BlogForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('blog:list')
    return render(request, 'blog/blog_form.html', {'form': form, 'heading': 'Создание статьи'})


@require_http_methods(['GET', 'POST'])
def blog_update(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    form = BlogForm(request.POST if request.method == 'POST' else None, instance=blog)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('blog:list')
    return render(request, 'blog/blog_form.html', {'form': form, 'heading': 'Редактирование статьи'})


@require_http_methods(['GET', 'POST'])
def blog_delete(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    if request.method == 'POST':
        blog.delete()
        return redirect('blog:list')
    return render(request, 'blog/blog_confirm_delete.html', {'blog': blog})
