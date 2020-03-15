from django.shortcuts import render, get_object_or_404, redirect
from .models import Subscription, Post, User
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .tasks import send_mail_delay
from test_proj.settings import EMAIL_HOST_USER

class UserView(View):
    template_name = 'blog/blog_user_account.html'


    def get(self, request, username, *args, **kwargs):
        user = get_object_or_404(User, username=username)
        user_request = request.user
        posts = Post.objects.filter(author=user).order_by('-created')
        subscribers_number = Subscription.objects.filter(author=user).count()
        subscription_number = Subscription.objects.filter(subscriber=user).count()

        subscription = False
        if user_request.is_authenticated and user.username != user_request.username:
            subscription = True if len(Subscription.objects.filter(author=user, subscriber=user_request)) else False

        context = {
            'user': user,
            'requested_user': user_request,
            'posts': posts,
            'subscribers_number': subscribers_number,
            'subscription_number': subscription_number,
            'subscription': subscription,
        }

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        user = request.user
        if 'title' in request.POST and 'content' in request.POST:
            title = request.POST['title']
            content = request.POST['content']


            Post(title=title, content=content, author=user).save()

            email_html_path = 'blog/email_subscription.html'
            text = 'New post'
            topic = 'New post created!'
            from_send = EMAIL_HOST_USER
            to_send = [subscription.subscriber.email for subscription in Subscription.objects.filter(author=user)]
            task = send_mail_delay.delay(email_html_path, from_send, to_send, topic, text)

        elif 'action' in request.POST:
            author = request.POST['author']
            subscriber = request.POST['subscriber']
            author_obj = get_object_or_404(User, username=author)
            subscriber_obj = get_object_or_404(User, username=subscriber)
            action = request.POST['action']

            if action == 'Subscribe':
                Subscription(author=author_obj, subscriber=subscriber_obj).save()
            elif action == 'Unsubscribe':
                posts = Post.objects.filter(author=author_obj)
                for post in posts:
                    post.read_by.remove(subscriber_obj)
                Subscription.objects.filter(author=author_obj, subscriber=subscriber_obj).delete()

            return redirect('blog:user_view', username=author)

        return redirect('blog:user_view', username=user.username)

class PostsView(LoginRequiredMixin, View):
    template_name = 'blog/blog_posts.html'
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        user = request.user
        subscriptions = [subscription.author for subscription in Subscription.objects.filter(subscriber=user)]
        posts = Post.objects.filter(author__in=subscriptions).order_by('-created')
        print([post.read_by.all() for post in posts])
        context = {
            'posts': posts,
            'user': user,
        }

        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        user = request.user
        if 'read' in request.POST:
            post_id = request.POST['post_id']

            post = get_object_or_404(Post, id=post_id)
            post.read_by.add(user)

        return redirect('blog:posts_view')
