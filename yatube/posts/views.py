from django.shortcuts import render

# Create your views here.
def group_posts(request, slug):
    template = 'posts/group_list.html'
    return render(request, template)