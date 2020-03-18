from django.urls import reverse, resolve

class TestUrls:

    def test_posts_url(self):
        path = reverse('blog:posts_view')
        assert resolve(path).view_name == 'blog:posts_view'

    def test_main_page_url(self):
        path = reverse('blog:main_page')
        assert resolve(path).view_name == 'blog:main_page'

    def test_post_url(self):
        path = reverse('blog:post_view', kwargs={'post_id': 1})
        assert resolve(path).view_name == 'blog:post_view'

    def test_user_url(self):
        path = reverse('blog:user_view', kwargs={'username': 'admin'})
        assert resolve(path).view_name == 'blog:user_view'