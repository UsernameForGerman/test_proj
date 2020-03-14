from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect, reverse
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.urls import reverse_lazy
from .models import Subscription, Post, User
from django.views import View

class UserView(View):
    template_name = 'blog/blog_user_account.html'


    def get(self, request, username, *args, **kwargs):
        user = get_object_or_404(User, username=username)
        user_request = request.user
        posts = Post.objects.filter(author=user)
        subscribers_number = Subscription.objects.filter(author=user).count()
        subscription_number = Subscription.objects.filter(subscriber=user).count()

        context = {
            'user': user,
            'requested_user': user_request,
            'posts': posts,
            'subscribers_number': subscribers_number,
            'subscription_number': subscription_number,
        }

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        if 'title' in request.POST and 'content' in request.POST:
            title = request.POST['title']
            content = request.POST['content']
            user = request.user

            Post(title=title, content=content, author=user).save()

        return redirect('blog:user_view', username=user.username)

class PostsView(View):
    template_name = ''

    def get(self, *args, **kwargs):
        return

    def post(self, *args, **kwargs):
        return