from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Post, Group

# Create your views here.
def index(request):
    posts = Post.objects.order_by('-pub_date')[:10]    
    context = {
        'posts': posts,
    }
    return render(request, 'posts/index.html', context) 


# В урл мы ждем парметр, и нужно его прередать в функцию для использования
def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by('-pub_date')[:10]
    template = 'posts/group_list.html'    
    context = {      
        'group': group,
        'posts': posts,
    }
    return render(request, template, context)


