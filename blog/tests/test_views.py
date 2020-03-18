from django.urls import reverse
from django.test import RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from mixer.backend.django import mixer
from blog.views import PostsView, UserView, MainPageView, PostView
from django.test import TestCase
from blog.models import Post, Subscription
import pytest
from blog.admin import PostAdmin
from django.contrib.admin.sites import AdminSite




@pytest.mark.parametrize('url_name, url_kwargs, req_type',
    [
        ('blog:posts_view', None, 'get'),
        ('blog:posts_view', None, 'post'),
        ('blog:user_view', {'username': 'admin'}, 'post'),
        ('blog:post_view', {'post_id': 1}, 'get'),
    ],
)
def test_protected_views(client, url_name, url_kwargs, req_type):
    """Verify meme views are protected from unauthenticated access"""
    url = reverse(url_name, kwargs=url_kwargs)
    resp = client.get(url) if req_type == 'get' else client.post(url)
    assert resp.status_code == 302
    assert resp.url.startswith(reverse('login'))

@pytest.mark.django_db
def test_main_page(rf):
    url = reverse('blog:main_page')
    request = rf.get(url)
    request.user = AnonymousUser()
    response = MainPageView().get(request)

    assert response.status_code == 200

    user = mixer.blend(User, username='user')
    request.user = user
    response = MainPageView().get(request)

    assert response.status_code == 302
    assert response.url == reverse('blog:posts_view')

@pytest.mark.django_db
def test_post_view(rf):
    post = mixer.blend(Post, author=mixer.blend(User, username='admin'))
    user = mixer.blend(User, username='user')
    url = reverse('blog:post_view', kwargs={'post_id': post.id})

    request = rf.get(url)
    request.user = user

    response = PostView().get(request, post_id=post.id)

    assert response.status_code == 302
    assert response.url == reverse('blog:user_view', kwargs={'username': post.author.username})

    mixer.blend(Subscription, author=post.author, subscriber=user)

    response = PostView().get(request, post_id=post.id)
    assert response.status_code == 200



"""
@pytest.fixture(scope='module')
def factory():
    return RequestFactory()

@pytest.fixture
def user(request, db):
    return mixer.blend(User, username=request.param)


@pytest.mark.parametrize('user', ['user'], indirect=True)
def test_user_view_unauthenticated(factory, user):
    mixer.blend(User, username='admin')
    path = reverse('blog:user_view', kwargs={'username': 'admin'})
    request = factory.get(path)
    request.user = user

    response = UserView().get(request=request, username='admin')
    assert response.status_code == 200
"""

@pytest.mark.django_db
class TestUserView(TestCase):

    @classmethod
    def setUpClass(self):
        super(TestUserView, self).setUpClass()
        self.admin = mixer.blend(User, username='admin')
        self.user = mixer.blend(User, username='user')
        self.factory = RequestFactory()
        self.path = reverse('blog:user_view', kwargs={'username': 'admin'})
        self.anonymous_user = AnonymousUser()


    def test_user_view_authenticated(self):
        request = self.factory.get(self.path)
        request.user = self.user

        response = UserView().get(request=request, username='admin')
        assert response.status_code == 200

    def test_get_user_view_unauthenticated(self):
        request = self.factory.get(self.path)
        request.user = self.anonymous_user

        response = UserView().get(request=request, username='admin')
        assert response.status_code == 200

    def test_get_user_view_another_authenticated(self):
        request = self.factory.get(self.path)
        request.user = self.user

        response = UserView().get(request=request, username='admin')
        assert response.status_code == 200

    def test_create_post(self):
        request = self.factory.post(
            self.path,
            {
                'title': 'title1',
                'content': 'content1',
            },
            kwargs={'username': self.admin.username},
        )

        request.user = self.user
        response = UserView().post(request=request, username=self.admin.username)

        assert response.status_code == 302
        assert response.url == reverse('blog:user_view', kwargs={'username': self.admin.username})

        # TODO: google tasks delayed check
        """
        request.user = self.admin
        response = UserView().post(request=request, username=self.admin.username)

        assert response.status_code == 302
        assert response.url == reverse('blog:user_view', kwargs={'username': self.admin.username})
        assert Post.objects.filter(author=self.admin).count() == 1
        assert (
            Post.objects.filter(author=self.admin).exists()
        )
        """


    def test_subscribe(self):
        request = self.factory.post(
            self.path,
            {
                'action': 'Subscribe',
                'author': self.admin.username,
                'subscriber': self.user.username,
            },
            kwargs={'username': self.admin.username},
        )

        request.user = self.user
        response = UserView().post(request=request, username=self.admin.username)

        assert response.status_code == 302
        assert response.url == reverse('blog:user_view', kwargs={'username': self.admin.username})
        assert Subscription.objects.filter(author=self.admin).count() == 1
        assert (
            Subscription.objects.filter(author=self.admin, subscriber=self.user).exists()
        )

        # if sub already exists
        response = UserView().post(request=request, username=self.admin.username)
        assert response.status_code == 302
        assert response.url == reverse('blog:user_view', kwargs={'username': self.admin.username})
        assert Subscription.objects.filter(author=self.admin).count() == 1
        assert (
            Subscription.objects.filter(author=self.admin, subscriber=self.user).exists()
        )

    def test_unsubscribe(self):
        request = self.factory.post(
            self.path,
            {
                'action': 'Unsubscribe',
            },
            kwargs={'username': self.admin.username},
        )

        request.user = self.user
        response = UserView().post(request=request, username=self.admin.username)

        assert response.status_code == 302
        assert response.url == reverse('blog:user_view', kwargs={'username': self.admin.username})

        mixer.blend(Subscription, author=self.admin, subscriber=self.user)
        post = mixer.blend(Post, author=self.admin)
        post.read_by.add(self.user)

        response = UserView().post(request=request, username=self.admin.username)


        assert response.status_code == 302
        assert response.url == reverse('blog:user_view', kwargs={'username': self.admin.username})
        assert Subscription.objects.filter(author=self.admin, subscriber=self.user).count() == 0
        assert not self.user.user_read.filter(author=self.admin).exists()
        assert not (
            Subscription.objects.filter(author=self.admin, subscriber=self.user).exists()
        )


@pytest.mark.django_db
class TestPostsView(TestCase):

    @classmethod
    def setUpClass(self):
        super(TestPostsView, self).setUpClass()
        self.author_user = mixer.blend(User, username='admin')
        self.user = mixer.blend(User, username='user')
        self.post = mixer.blend('blog.Post', author=self.author_user)
        self.path = reverse('blog:posts_view')
        self.factory = RequestFactory()
        self.anonymous_user = AnonymousUser()

    def test_get_posts_view_authenticated(self):
        request = self.factory.get(self.path)
        request.user = self.user

        response = PostsView().get(request=request)
        assert response.status_code == 200

    def test_read_mark(self):

        request = self.factory.post(self.path, {
            'read': 'Read',
            'post_id': self.post.id,
        })
        request.user = self.user

        response = PostsView().post(request=request)

        assert response.status_code == 302
        assert response.url == reverse('blog:posts_view')
        assert self.user not in self.post.read_by.all()

        self.subscription = mixer.blend('blog.Subscription', author=self.author_user, subscriber=self.user)

        response = PostsView().post(request=request)
        assert response.status_code == 302
        assert response.url == reverse('blog:posts_view')
        assert self.user in self.post.read_by.all()

    #TODO: google tasks delayed check
    """
    def test_admin_post_creation(self):
        admin_post_model = PostAdmin(model=Post, admin_site=AdminSite())
        new_post = Post(author=self.user, title='title', content='content')
        request = self.factory.get('/admin')
        request.user = User.objects.create_superuser('username', None, 'password')
        admin_post_model.save_model(obj=new_post, request=request, form=None, change=None)

        assert Post.objects.filter(author=self.user).exists()
    """






