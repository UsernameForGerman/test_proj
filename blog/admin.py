from django.contrib import admin
from .models import Post, Subscription
from .tasks import send_mail_delay
from test_proj.settings import EMAIL_HOST_USER

# Register your models here.

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        user = obj.author

        super().save_model(request, obj, form, change)

        post_id = obj.id

        email_html_path = 'blog/email_subscription.html'
        text = 'New post'
        topic = 'New post created!'
        from_send = EMAIL_HOST_USER
        to_send = [subscription.subscriber.email for subscription in Subscription.objects.filter(author=user)]
        url = request.get_host() + '/posts' + '/{}'.format(post_id)
        context = {
            'url': url,
        }
        task = send_mail_delay.delay(email_html_path, from_send, to_send, topic, text, context)



# admin.site.register(Post)
