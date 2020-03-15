from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author')
    read_by = models.ManyToManyField(User, default=None, related_name='user_read', blank=True)

    def __str__(self):
        return self.title + ' - ' + str(self.author)

class Subscription(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='main_user')
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriber')

    def __str__(self):
        return str(self.author) + ' - ' + str(self.subscriber)

