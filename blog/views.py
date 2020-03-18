from django.shortcuts import render, get_object_or_404, redirect
from .models import Subscription, Post, User
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from .tasks import send_mail_delay
from test_proj.settings import EMAIL_HOST_USER
from .forms import PostForm

class UserView(View):
    template_name = 'blog/blog_user_account.html'
    login_url = '/login/'

    def get(self, request, username, *args, **kwargs):
        user_request = get_object_or_404(User, username=username)
        user = request.user
        posts = Post.objects.filter(author=user_request).order_by('-created')
        subscribers_number = Subscription.objects.filter(author=user_request).count()
        subscription_number = Subscription.objects.filter(subscriber=user_request).count()

        subscription = False
        if user.is_authenticated and user.username != user_request.username:
            subscription = True if len(Subscription.objects.filter(author=user_request, subscriber=user)) else False

        users = User.objects.exclude(username=request.user.username)


        context = {
            'users': users,
            'user': user,
            'requested_user': user_request,
            'posts': posts,
            'subscribers_number': subscribers_number,
            'subscription_number': subscription_number,
            'subscription': subscription,
        }

        return render(request, self.template_name, context=context)

    @method_decorator(login_required(login_url=login_url))
    def post(self, request, username, *args, **kwargs):
        user = request.user
        if 'title' in request.POST and 'content' in request.POST and user.username == username:

            form = PostForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = user
                post.save()

                email_html_path = 'blog/email_subscription.html'
                text = 'New post'
                topic = 'New post created!'
                from_send = EMAIL_HOST_USER
                to_send = [subscription.subscriber.email for subscription in Subscription.objects.filter(author=user)]
                url = request.get_host() + '/posts' + '/{}'.format(post.id)
                context = {
                    'url': url,
                }
                task = send_mail_delay.delay(email_html_path, from_send, to_send, topic, text, context)

        elif 'action' in request.POST and user.username != username:
            author_obj = get_object_or_404(User, username=username)
            action = request.POST['action']
            subscription_objs = Subscription.objects.filter(author=author_obj, subscriber=user)

            if action == 'Subscribe':
                if len(subscription_objs):
                    return redirect('blog:user_view', username=username)
                Subscription(author=author_obj, subscriber=user).save()
            elif action == 'Unsubscribe':
                if len(subscription_objs):
                    posts = Post.objects.filter(author=author_obj)
                    for post in posts:
                        post.read_by.remove(user)
                    subscription_objs.delete()

            return redirect('blog:user_view', username=username)

        return redirect('blog:user_view', username=username)


class PostsView(View):
    template_name = 'blog/blog_posts.html'
    login_url = '/login/'

    @method_decorator(login_required(login_url=login_url))
    def get(self, request, *args, **kwargs):
        user = request.user
        subscriptions = [subscription.author for subscription in Subscription.objects.filter(subscriber=user)]
        posts = Post.objects.filter(author__in=subscriptions).order_by('-created')
        users = User.objects.exclude(username=request.user.username)

        context = {
            'posts': posts,
            'user': user,
            'users': users,
        }

        return render(request, self.template_name, context=context)

    @method_decorator(login_required(login_url=login_url))
    def post(self, request, *args, **kwargs):
        user = request.user
        if 'read' in request.POST:
            post_id = request.POST['post_id']
            post = get_object_or_404(Post, id=post_id)
            subscription_query = Subscription.objects.filter(author=post.author, subscriber=user)
            if len(subscription_query):
                post.read_by.add(user)
                post.save()


        return redirect('blog:posts_view')

class MainPageView(View):
    template_name = 'blog/main_page.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('blog:posts_view')
        else:
            return render(request, self.template_name)

class PostView(View):
    template_name = 'blog/blog_post_view.html'
    login_url = '/login/'

    @method_decorator(login_required(login_url=login_url))
    def get(self, request, post_id, *args, **kwargs):
        post = get_object_or_404(Post, id=post_id)

        user =request.user
        if len(Subscription.objects.filter(author=post.author, subscriber=user)):
            context = {
                'post': post,
            }

            return render(request, self.template_name, context=context)
        else:
            return redirect('blog:user_view', username=post.author)