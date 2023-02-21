from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache

from ..models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.author = User.objects.create_user(username='auth')
        cls.no_name_user = User.objects.create_user(username='no_name')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=PostURLTests.author,
            group=PostURLTests.group,
        )

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.no_name_user)
        self.authorized_author_client = Client()
        self.authorized_author_client.force_login(PostURLTests.author)

    def test_create_edit_post_urls_redirect_anonymous_on_user_login(self):
        """Неавторизованный пользователь, при попытке
        создания или редактирования поста,
        переадресуется на страницу авторизации"""
        urls_redirects = {
            reverse('posts:post_create'):
            reverse('users:login') + '?next=' + reverse('posts:post_create'),

            reverse(
                'posts:post_edit', args=(PostURLTests.post.id,)):
            reverse('users:login') + '?next=' + reverse(
                'posts:post_edit', args=(PostURLTests.post.id,))
        }
        for adress, redirect in urls_redirects.items():
            with self.subTest(adress=adress):
                response = self.client.get(adress, follow=True)
                self.assertRedirects(response, redirect)

    def test_edit_post_url_redirect_no_name_on_post_detail(self):
        """Если пользователь не автор поста,
        то он переадресуется на страницу с детальной информацией о посте"""
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    args=(PostURLTests.post.id,)), follow=True)
        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=(PostURLTests.post.id,))
        )

    def test_urls_uses_correct_template(self):
        """URL-адреса используют соответствующие шаблоны."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html'
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_author_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_unexisting_urls_get_404(self):
        """Выдается статус 404 при переходе на несуществующую страницу"""
        clients = (
            self.client,
            self.authorized_client,
            self.authorized_author_client,
        )
        for client in clients:
            with self.subTest(client=client):
                response = client.get('/unexisting_page/')
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_existing_url_get_200(self):
        """Выдается статус 200 при переходе на существующую страницу"""
        clients = (
            self.client,
            self.authorized_client,
            self.authorized_author_client,
        )
        urls = (
            reverse('posts:index'),
            reverse(
                'posts:group_list', args=(PostURLTests.group.slug,)
            ),
            reverse(
                'posts:profile', args=(PostURLTests.author.username,)
            ),
            reverse(
                'posts:post_detail', args=(PostURLTests.post.id,)
            )
        )
        for client in clients:
            with self.subTest(client=client):
                for url in urls:
                    with self.subTest(url=url):
                        response = client.get(url)
                        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_urls_get_302(self):
        """Выдается статус 302 при переходе страницу с переадресацией"""
        clients_url_names = {
            self.client: reverse('posts:post_create'),
            self.authorized_client: reverse(
                'posts:post_edit', args=(PostURLTests.post.id,)
            ),
        }
        for client, adress in clients_url_names.items():
            with self.subTest(client=client):
                response = client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_create_comment_url_redirect_anonymous_on_user_login(self):
        response = self.client.get(
            reverse('posts:add_comment',
                    args=(PostURLTests.post.id,)), follow=True)
        self.assertRedirects(
            response,
            reverse('users:login') + '?next='
            + reverse('posts:add_comment', args=(PostURLTests.post.id,))
        )
