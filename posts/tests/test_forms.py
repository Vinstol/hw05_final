import shutil

import tempfile

from django.conf import settings

from django.contrib.auth import get_user_model

from django.core.files.uploadedfile import SimpleUploadedFile

from django.test import Client
from django.test import TestCase
from django.test import override_settings

from django.urls import reverse

from posts.models import Group
from posts.models import Post

# from yatube.settings import BASE_DIR
# from yatube.settings import MEDIA_ROOT

# settings.MEDIA_ROOT = tempfile.mkdtemp(
# prefix='pages_',
# dir=settings.BASE_DIR
# )


@override_settings()
# @override_settings(ROOT_URLCONF=settings.MEDIA_ROOT)
# @override_settings(MEDIA_ROOT=settings.MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(
            prefix='pages_',
            dir=settings.BASE_DIR
        )

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        User = get_user_model()
        cls.user = User.objects.create(username='Polzovatel')

        cls.test_group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

        cls.test_post = Post.objects.create(
            text='Тестовое сообщение!!!',
            author=cls.user,
            group=cls.test_group,
            image=uploaded
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_new_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': self.test_post.text,
            'author': self.test_post.author,
            'group': self.test_group.id,
            'image': self.test_post.image,
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        new_post = Post.objects.last()
        self.assertTrue(new_post)

        self.assertEqual(new_post.text, PostFormTests.test_post.text)
        self.assertEqual(new_post.author, PostFormTests.test_post.author)
        self.assertEqual(new_post.group, PostFormTests.test_group)
        self.assertEqual(new_post.image, PostFormTests.test_post.image)

    def test_post_edit(self):
        """Валидная форма редактирует существующую запись в Post."""
        posts_count = Post.objects.count()
        edit_post = PostFormTests.test_post
        form_new_data = {
            'text': 'Новый текст',
            'author': self.user,
            'group': self.test_group.id,
        }
        response = self.authorized_client.post(
            reverse('post_edit', kwargs={
                'username': self.user,
                'post_id': edit_post.id
            }),
            data=form_new_data,
            follow=True
        )
        self.assertRedirects(response, reverse('post_view', kwargs={
            'username': self.user,
            'post_id': edit_post.id
        }))

        self.assertEqual(Post.objects.count(), posts_count)
        new_post = Post.objects.last()
        self.assertTrue(new_post)
        self.assertEqual(new_post.text, form_new_data['text'])
        self.assertEqual(new_post.author, form_new_data['author'])
        self.assertEqual(new_post.group.id, form_new_data['group'])
