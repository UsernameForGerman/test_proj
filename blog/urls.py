from django.urls import re_path, path
from .views import UserView, PostsView, MainPageView, PostView

app_name = 'blog'

#TODO: correct rules of username string within Django's rules for username
urlpatterns = [
    path('', MainPageView.as_view(), name='main_page'),
    path('posts/', PostsView.as_view(), name='posts_view'),
    re_path(r'^posts/(?P<post_id>[a-zA-Z0-9_.-]*)$', PostView.as_view(), name='post_view'),
    re_path(r'^user/(?P<username>[a-zA-Z0-9_.-]*)$', UserView.as_view(), name='user_view'),
]