from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from .forms import PostForm
from .models import Post, Group, User
from .utils import paginator


def index(request):
    post_list = Post.objects.order_by('-pub_date')
    page_obj = paginator(request, posts=post_list)
    template = 'posts/index.html'
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by('-pub_date')
    page_obj = paginator(request, posts=posts)
    template = 'posts/group_list.html'
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author).select_related('group')
    page_obj = paginator(request, posts=posts)
    template = 'posts/profile.html'
    count = Post.objects.filter(author=author).count()
    context = {
        'author': author,
        'page_obj': page_obj,
        'count': count
    }
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    count = Post.objects.filter(
        author__username=post.author.username).count()
    template = 'posts/post_detail.html'
    context = {
        'post': post,
        'count': count
    }
    return render(request, template, context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=post.author.username)
    template = 'posts/create_post.html'
    context = {
        'form': form
    }
    return render(request, template, context)

# Добавил в контекст 'is_edit': True и проверку на него в шаблоне
# Сейчас проект отрабатвает корректно. Согласно заданию.
# Если сделать редирект на вьюху post_create, то будет
# перенаправление на создание нового поста, что противоречит задаче.
# И тесты соответственно не пропускают проект.


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST or None, instance=post)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    if form.is_valid():
        template = 'posts:post_detail'
        form.save()
        return redirect(template, post_id=post.pk)
    template = 'posts/create_post.html'
    context = {
        'form': form,
        'is_edit': True
    }
    return render(request, template, context)
