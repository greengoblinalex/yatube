import shutil
import tempfile

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Post, Group, User
from .. import constants

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
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
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=PostPagesTests.user,
            group=PostPagesTests.group,
            image=PostPagesTests.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
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
                        if attribute == 'page_obj':
                            first_object = response.context[attribute][0]
                            page_obj_text_0 = first_object.text
                            page_obj_author_0 = first_object.author
                            page_obj_group_0 = first_object.group
                            page_obj_group_id_0 = first_object.group.id
                            page_obj_image_0 = first_object.image
                            self.assertEqual(
                                page_obj_text_0, PostPagesTests.post.text)
                            self.assertEqual(
                                page_obj_author_0, PostPagesTests.user)
                            self.assertEqual(
                                page_obj_group_0, PostPagesTests.group)
                            self.assertEqual(
                                page_obj_group_id_0, PostPagesTests.group.id)
                            self.assertTrue(page_obj_image_0)

                        elif attribute == 'group':
                            first_object = response.context[attribute]
                            group_title_0 = first_object.title
                            group_slug_0 = first_object.slug
                            group_description_0 = first_object.description
                            group_id_0 = first_object.id
                            self.assertEqual(
                                group_title_0, PostPagesTests.group.title)
                            self.assertEqual(
                                group_slug_0, PostPagesTests.group.slug)
                            self.assertEqual(
                                group_description_0,
                                PostPagesTests.group.description)
                            self.assertEqual(
                                group_id_0, PostPagesTests.group.id)

                        elif attribute == 'author':
                            first_object = response.context[attribute]
                            author_username_0 = first_object.username
                            self.assertEqual(
                                author_username_0,
                                PostPagesTests.user.username)

                        elif attribute == 'post':
                            response = self.authorized_client.get(reverse_name)
                            first_object = response.context[attribute]
                            post_text_0 = first_object.text
                            post_author_0 = first_object.author
                            post_group_0 = first_object.group
                            post_image_0 = first_object.image
                            self.assertEqual(
                                post_text_0, PostPagesTests.post.text)
                            self.assertEqual(
                                post_author_0, PostPagesTests.user)
                            self.assertEqual(
                                post_group_0, PostPagesTests.group)
                            self.assertTrue(post_image_0)

                        elif attribute == 'form':
                            for value, expected in form_fields.items():
                                with self.subTest(value=value):
                                    response = self.authorized_client.get(
                                        reverse_name)
                                    form_field = response.context.get(
                                        attribute).fields.get(value)
                                    self.assertIsInstance(form_field, expected)


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
        cls.post = Post.objects.create(
            author=OnCreatePostTests.user,
            text='Тестовый пост ',
            group=OnCreatePostTests.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(OnCreatePostTests.user)

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
