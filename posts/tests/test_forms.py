import shutil
import tempfile

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Post, Group, User, Comment
from ..constants import BYTE_IMAGE

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.changing_group = Group.objects.create(
            title='Группа для изменения',
            slug='changing-group-slug',
            description='Описание группы для изменения',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=TaskCreateFormTests.user,
            group=TaskCreateFormTests.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(TaskCreateFormTests.user)

    def test_create_new_post(self):
        """Проверяем, что корректно создается новый пост"""
        posts_id = [i.id for i in Post.objects.all()]
        uploaded = SimpleUploadedFile(
            name='test_image_1.jpeg',
            content=BYTE_IMAGE,
            content_type='image/jpeg'
        )
        form_data = {
            'text': 'Текст из формы',
            'group': TaskCreateFormTests.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        diff = Post.objects.exclude(id__in=posts_id)
        self.assertEqual(len(diff), 1)
        self.assertEqual(diff[0].author, response.wsgi_request.user)
        self.assertEqual(diff[0].text, form_data['text'])
        self.assertEqual(diff[0].group.id, form_data['group'])
        self.assertEqual(diff[0].image, 'posts/test_image_1.jpeg')

    def test_edit_post(self):
        """Проверяем, что пост редактируется корректно"""
        uploaded = SimpleUploadedFile(
            name='test_image_2.jpeg',
            content=BYTE_IMAGE,
            content_type='image/jpeg'
        )
        form_data = {
            'text': 'Текст из формы',
            'group': TaskCreateFormTests.changing_group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    args=(TaskCreateFormTests.post.id,)),
            data=form_data,
            follow=True
        )
        new_post = Post.objects.get(id=TaskCreateFormTests.post.id)
        self.assertEqual(new_post.author, response.wsgi_request.user)
        self.assertEqual(new_post.text, form_data['text'])
        self.assertEqual(new_post.group.id, form_data['group'])
        self.assertEqual(new_post.image, 'posts/test_image_2.jpeg')

    def test_create_comment(self):
        """После успешной отправки комментарий появляется на странице поста"""
        form_data = {
            'text': 'Текст из формы',
        }
        self.authorized_client.post(
            reverse('posts:add_comment',
                    args=(TaskCreateFormTests.post.id,)),
            data=form_data,
            follow=True
        )
        comment = Comment.objects.get(text=form_data['text'])
        self.assertTrue(comment)
