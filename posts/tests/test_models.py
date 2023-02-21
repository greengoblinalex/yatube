from django.test import TestCase

from ..models import Group, Post, User
from .. import constants


class PostModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=PostModelTests.user,
            group=PostModelTests.group,
        )

    def test_models_have_correct_object_names(self):
        """У моделей корректно работает __str__."""
        model_texts = {
            str(PostModelTests.group): PostModelTests.group.title,
            str(PostModelTests.post): PostModelTests.post.text[
                :constants.NUMBER_OF_FIRST_LETTERS],
        }
        for model, expected_value in model_texts.items():
            with self.subTest(model=model):
                self.assertEqual(model, expected_value)

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTests.post
        field_verboses = {
            'text': 'Текст поста',
            'created': 'Дата создания'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTests.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)
