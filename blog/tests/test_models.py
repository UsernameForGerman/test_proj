from blog.models import Post, Subscription, User
import pytest
from mixer.backend.django import mixer

@pytest.mark.django_db
def test_str_post():
    post = mixer.blend(Post, title='title', author=mixer.blend(User, username='author'))
    assert str(post) == 'title - author'

@pytest.mark.django_db
def test_str_subscription():
    author = mixer.blend(User, username='author')
    subscriber = mixer.blend(User, username='subscriber')
    subscription = mixer.blend(Subscription, author=author, subscriber=subscriber)
    assert str(subscription) == 'author - subscriber'