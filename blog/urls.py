from django.contrib import admin
from django.urls import path, re_path, include
from .views import UserView

app_name = 'blog'

#TODO: correct rules of username string within Django's rules for username
urlpatterns = [
    re_path(r'^user/(?P<username>[a-zA-Z0-9_.-]*)$', UserView.as_view(), name='user_view')
]