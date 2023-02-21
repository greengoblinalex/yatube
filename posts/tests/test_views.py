import shutil
import tempfile

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

from ..models import Post, Group, User, Follow
from .. import constants
from . import helpers

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.following = User.objects.create_user(username='following')

        cls.following_group = Group.objects.create(
            title='Тестовая группа',
            slug='following-test-slug',
            description='Тестовое описание',
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.jpeg',
            content=constants.BYTE_IMAGE,
            content_type='image/jpeg'
        )

        cls.following_post = Post.objects.create(
            text='Пост для теста подписок',
            author=PostPagesTests.following,
            group=PostPagesTests.following_group,
            image=PostPagesTests.uploaded,
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=PostPagesTests.user,
            group=PostPagesTests.group,
            image=PostPagesTests.uploaded,
        )

        Follow.objects.create(
            user=PostPagesTests.user,
            author=PostPagesTests.following
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesTests.user)

    def test_pages_uses_correct_template(self):
        """Reverse-адреса используют соответствующие шаблоны."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',

            reverse(
                'posts:group_list',
                args=(PostPagesTests.group.slug,)): 'posts/group_list.html',

            reverse(
                'posts:profile',
                args=(PostPagesTests.user.username,)): 'posts/profile.html',

            reverse(
                'posts:post_detail',
                args=(PostPagesTests.post.id,)): 'posts/post_detail.html',

            reverse('posts:post_create'): 'posts/create_post.html',

            reverse(
                'posts:post_edit',
                args=(PostPagesTests.post.id,)): 'posts/create_post.html',

            reverse('posts:follow_index'): 'posts/follow.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_show_correct_context(self):
        """Шаблоны сформированы с правильным контекстом."""
        page_names_attributes = {
            reverse('posts:index'): ('page_obj',),

            reverse(
                'posts:group_list',
                args=(PostPagesTests.group.slug,)): ('group', 'page_obj',),

            reverse(
                'posts:profile',
                args=(PostPagesTests.user.username,)): ('author', 'page_obj',),

            reverse(
                'posts:post_detail',
                args=(PostPagesTests.post.id,)): ('post',),

            reverse('posts:post_create'): ('form',),

            reverse(
                'posts:post_edit',
                args=(PostPagesTests.post.id,)): ('form', 'post',),

            reverse('posts:follow_index'): ('page_obj',),
        }

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for reverse_name, attributes in page_names_attributes.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                for attribute in attributes:
                    with self.subTest(attribute=attribute):
                        helpers.helper_test_page_obj_attribute(
                            self, response, attribute,
                            reverse_name, PostPagesTests
                        )
                        helpers.helper_test_group_attribute(
                            self, response, attribute, PostPagesTests
                        )
                        helpers.helper_test_author_attribute(
                            self, response, attribute, PostPagesTests
                        )
                        helpers.helper_test_post_attribute(
                            self, response, attribute, PostPagesTests
                        )
                        helpers.helper_test_post_attribute(
                            self, response, attribute, PostPagesTests
                        )
                        helpers.helper_test_form_attribute(
                            self, form_fields, response, attribute
                        )

    def test_caching(self):
        """Кеширование работает"""
        new_post = Post.objects.create(
            text='Тестовый пост',
            author=PostPagesTests.user,
        )

        response = self.client.get(reverse('posts:index'))
        Post.objects.get(id=new_post.id).delete()
        response_after_delete_post = self.client.get(reverse('posts:index'))
        self.assertEqual(
            response.content,
            response_after_delete_post.content
        )

        cache.clear()
        response_after_clear_cache = self.client.get(reverse('posts:index'))
        self.assertNotEqual(
            response.content,
            response_after_clear_cache.content
        )

    def test_page_404_use_custom_templage(self):
        """Страница 404 выдает кастомный шаблон"""
        response = self.client.get('/unexisting_page/')
        self.assertTemplateUsed(response, 'core/404.html')


class PaginatorViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        post_list = [
            Post(
                author=PaginatorViewsTests.user,
                text='Тестовый пост ',
                group=PaginatorViewsTests.group,
            )
        ] * constants.NUMBER_OF_RECORS
        Post.objects.bulk_create(post_list)

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorViewsTests.user)

    def test_index_first_page_contains_ten_records(self):
        """index содержит 10 записей на первой странице"""
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(
            len(response.context['page_obj']),
            constants.NUMBER_OF_FIRST_PAGE_RECORS
        )

    def test_index_second_page_contains_three_records(self):
        """index содержит 3 записb на первой странице"""
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(
            len(response.context['page_obj']),
            constants.NUMBER_OF_SECOND_PAGE_RECORDS
        )

    def test_group_posts_first_page_contains_ten_records(self):
        """group_posts содержит 10 записей на первой странице"""
        response = self.client.get(
            reverse('posts:group_list', args=('test-slug',)))
        self.assertEqual(
            len(response.context['page_obj']),
            constants.NUMBER_OF_FIRST_PAGE_RECORS
        )

    def test_group_posts_second_page_contains_three_records(self):
        """group_posts содержит 3 записи на первой странице"""
        response = self.client.get(
            reverse('posts:group_list', args=('test-slug',)) + '?page=2'
        )
        self.assertEqual(
            len(response.context['page_obj']),
            constants.NUMBER_OF_SECOND_PAGE_RECORDS
        )

    def test_profile_first_page_contains_ten_records(self):
        """profile содержит 10 записей на первой странице"""
        response = self.client.get(
            reverse('posts:profile', args=('auth',))
        )
        self.assertEqual(
            len(response.context['page_obj']),
            constants.NUMBER_OF_FIRST_PAGE_RECORS
        )

    def test_profile_second_page_contains_three_records(self):
        """profile содержит 3 записи на первой странице"""
        response = self.client.get(
            reverse('posts:profile', args=('auth',)) + '?page=2'
        )
        self.assertEqual(
            len(response.context['page_obj']),
            constants.NUMBER_OF_SECOND_PAGE_RECORDS
        )


class OnCreatePostTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.following = User.objects.create_user(username='following')
        cls.not_follower = User.objects.create_user(username='not_follower')

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.non_test_group = Group.objects.create(
            title='Тестовая группа',
            slug='non-test-slug',
            description='Тестовое описание',
        )

        cls.following_post = Post.objects.create(
            author=OnCreatePostTests.following,
            text='Пост для теста подписок',
        )
        cls.post = Post.objects.create(
            author=OnCreatePostTests.user,
            text='Тестовый пост ',
            group=OnCreatePostTests.group,
        )

        Follow.objects.create(
            user=OnCreatePostTests.user,
            author=OnCreatePostTests.following
        )

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(OnCreatePostTests.user)
        self.authorized_not_follower_client = Client()
        self.authorized_not_follower_client.force_login(
            OnCreatePostTests.not_follower)

    def test_post_on_index_page(self):
        """Созданный пост есть на главной странице"""
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(
            response.context.get('page_obj')[0],
            OnCreatePostTests.post
        )

    def test_post_on_post_group_page(self):
        """Созданный пост есть на странице группы"""
        response = self.client.get(
            reverse('posts:group_list', args=(OnCreatePostTests.group.slug,)))
        self.assertEqual(
            response.context.get('page_obj')[0],
            OnCreatePostTests.post
        )

    def test_post_not_on_another_post_group_page(self):
        """Созданного поста нет группе, к которой пост не относится"""
        response = self.client.get(
            reverse('posts:group_list', args=('non-test-slug',)))
        for i in response.context.get('page_obj'):
            with self.subTest(i=i):
                self.assertNotEqual(i, OnCreatePostTests.post)

    def test_post_on_author_profile_page(self):
        """Созданный пост находится на странице автора"""
        response = self.client.get(
            reverse('posts:profile', args=('auth',)))
        self.assertEqual(
            response.context.get('page_obj')[0],
            OnCreatePostTests.post
        )

    def test_only_followers_has_following_posts(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех,
        кто не подписан."""
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(
            response.context.get('page_obj')[0],
            OnCreatePostTests.following_post
        )

        response = self.authorized_not_follower_client.get(
            reverse('posts:follow_index'))
        self.assertEqual(len(response.context.get('page_obj')), 0)
