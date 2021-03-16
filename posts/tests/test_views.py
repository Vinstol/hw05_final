import shutil

import tempfile

import time

from django import forms

from django.conf import settings

from django.contrib.auth import get_user_model

from django.core.files.uploadedfile import SimpleUploadedFile

from django.test import Client
from django.test import TestCase

from django.urls import reverse

from posts.models import Follow, Group
from posts.models import Post

from yatube.settings import POSTS_LIMIT


class PostPagesTest(TestCase):
    ''' Создание экземпляров моделей Post и Group'''
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(
            prefix='pages_',
            dir=settings.BASE_DIR
        )

        User = get_user_model()
        cls.test_user = User.objects.create(username='Polzovatel')
        cls.ok_group = Group.objects.create(
            title='Правильная тестовая группа',
            slug='ok-slug',
            description='Описание правильной группы'
        )
        cls.wrong_group = Group.objects.create(
            title='Другая тестовая группа',
            slug='wrong-slug',
            description='Описание другой группы'
        )
        cls.test_post = Post.objects.create(
            text='Тестовое сообщение!!!',
            pub_date='2011-05-11',
            author=cls.test_user,
            group=cls.ok_group
        )
        
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        """ Создание неавторизованного клиента и
        клиента с авторизованным пользователем"""
        self.guest_client = Client()

        user_1 = get_user_model()
        self.user_1 = user_1.objects.get(username='Polzovatel')
        self.authorized_client_1 = Client()
        self.authorized_client_1.force_login(self.user_1)

        user_2 = get_user_model()
        self.user_2 = user_2.objects.create(username='Katamaranov')
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            'index.html': reverse('index'),
            'group.html': reverse(
                'group',
                kwargs={'slug': self.ok_group.slug}
            ),
            'new_post.html': reverse('new_post'),
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client_1.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Проверка передачи в шаблоны корректного контекста
    def test_index_page_show_correct_context(self):
        """View-функция страницы index передает правильный контекст."""
        response = self.authorized_client_1.get(reverse('index'))

        test_post_text = response.context.get('page')[0].text
        test_post_author = response.context.get('page')[0].author.username
        test_post_group = response.context.get('page')[0].group.title

        self.assertEqual(test_post_text, 'Тестовое сообщение!!!')
        self.assertEqual(test_post_author, 'Polzovatel')
        self.assertEqual(test_post_group, 'Правильная тестовая группа')

    def test_group_page_show_correct_context(self):
        """View-функция страницы group передает правильный контекст."""
        response = self.authorized_client_1.get(
            reverse('group', kwargs={'slug': self.ok_group.slug})
        )

        test_group_title = response.context.get('group').title
        test_group_slug = response.context.get('group').slug
        test_group_description = response.context.get('group').description

        self.assertEqual(test_group_title, 'Правильная тестовая группа')
        self.assertEqual(test_group_slug, 'ok-slug')
        self.assertEqual(test_group_description, 'Описание правильной группы')

    def test_new_post_page_show_correct_context(self):
        """View-функция страницы new_post передает правильный контекст."""
        response = self.authorized_client_1.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for field_name, field_format in form_fields.items():
            with self.subTest(value=field_name):
                form_field = (
                    response.context.get('form').fields.get(field_name)
                )
                self.assertIsInstance(form_field, field_format)

    def test_profile_page_show_correct_context(self):
        """View-функция страницы профайла передает правильный контекст."""
        response = self.authorized_client_2.get(reverse('profile', kwargs={
            'username': self.test_post.author
        }))

        test_profile_posts = response.context.get('page')[0].text
        test_profile_group = response.context.get('page')[0].group.title
        test_profile_posts_cnt = response.context.get('posts_cnt')

        self.assertEqual(test_profile_posts, 'Тестовое сообщение!!!')
        self.assertEqual(test_profile_group, 'Правильная тестовая группа')
        self.assertEqual(test_profile_posts_cnt, 1)

    def test_post_view_show_correct_context(self):
        """View-функция страницы поста передает правильный контекст."""
        response = self.authorized_client_2.get(reverse('post_view', kwargs={
            'username': self.test_post.author,
            'post_id': self.test_post.id
        }))

        post_view_text = response.context.get('post').text
        post_view_group = response.context.get('post').group.title
        self.assertEqual(post_view_text, 'Тестовое сообщение!!!')
        self.assertEqual(post_view_group, 'Правильная тестовая группа')

    def test_post_edit_page_show_correct_context(self):
        """View-функция редактирования поста передает правильный контекст."""
        response = self.authorized_client_1.get(reverse('post_edit', kwargs={
            'username': self.test_post.author,
            'post_id': self.test_post.id
        }))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for field_name, field_format in form_fields.items():
            with self.subTest(value=field_name):
                form_field = (
                    response.context.get('form').fields.get(field_name)
                )
                self.assertIsInstance(form_field, field_format)

    def test_post_in_right_group(self):
        """Пост попал в нужную группу"""
        groups_list = {
            'ok_group': reverse('group', kwargs={'slug': self.ok_group.slug}),
            'wrong_group': reverse(
                'group',
                kwargs={'slug': self.wrong_group.slug}
            )
        }
        for some_group, reverse_name in groups_list.items():
            with self.subTest():
                response = self.authorized_client_1.get(reverse_name)
                posts_in_group = response.context.get('page')
                if some_group == 'ok_group':
                    self.assertIn(self.test_post, posts_in_group)
                else:
                    self.assertNotIn(self.test_post, posts_in_group)

    def test_main_page_display_post(self):
        """Пост видно на главной странице"""
        response = self.authorized_client_1.get(reverse('index'))
        main_page_view = response.context.get('page')
        self.assertIn(self.test_post, main_page_view)

    def test_indext_page_list_is_1(self):
        """На стартовую страницу передаётся ожидаемое количество постов"""
        response = self.authorized_client_1.get(reverse('index'))
        self.assertTrue(len(response.context['page']) <= POSTS_LIMIT)

    def test_post_image_exists_in_context(self):
        """При выводе поста картинка предается в словаре context."""
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
        tim_group = Group.objects.create(
            title='Группа с картинками',
            slug='image-slug',
            description='Тут посты с картинками'
        )
        tim_post = Post.objects.create(
            text='Сообщение c картинкой',
            pub_date='2019-08-15',
            author=self.test_user,
            group=tim_group,
            image=uploaded
        )

        response_1 = self.authorized_client_1.get(reverse('index'))
        response_2 = self.authorized_client_1.get(reverse('group', kwargs={
            'slug': tim_group.slug
        }))
        response_3 = self.authorized_client_1.get(reverse('profile', kwargs={
            'username': tim_post.author
        }))
        response_4 = self.authorized_client_1.get(reverse('post_view', kwargs={
            'username': tim_post.author,
            'post_id': tim_post.id
        }))

        test_index_image = response_1.context.get('page')[0].image
        test_group_image = response_2.context.get('page')[0].image
        test_profile_image = response_3.context.get('page')[0].image
        test_post_view_image = response_4.context.get('post').image

        self.assertEqual(test_index_image, tim_post.image)
        self.assertEqual(test_group_image, tim_post.image)
        self.assertEqual(test_profile_image, tim_post.image)
        self.assertEqual(test_post_view_image, tim_post.image)

    # Проверка кэширования стартовой страницы
    def test_cached_index_page(self):
        """Стартовая страница сохранена в кэше."""
        cached_response_1 = self.authorized_client_1.get(reverse('index'))
       
        Post.objects.filter(id=self.test_post.id).delete()
        cached_response_2 = self.authorized_client_1.get(reverse('index'))
        self.assertEqual(cached_response_1.content, cached_response_2.content)

        time.sleep(20)
        cached_response_3 = self.authorized_client_1.get(reverse('index'))
        self.assertNotEqual(
            cached_response_1.content,
            cached_response_3.content
        )

    # Проверка работоcпособности подписки/отписки
    def test_follow(self):
        """При подписке создается соответствующая запись в БД."""
        self.authorized_client_1.get(reverse(
            'profile_follow',
            kwargs={'username': self.user_2}
        ))
        follow_exists = Follow.objects.filter(
            user=self.user_1,
            author=self.user_2
        ).exists()
        self.assertTrue(follow_exists)

    def test_unfollow(self):
        """При отписке удаляется соответствующая запись в БД."""
        self.authorized_client_1.get(reverse(
            'profile_follow',
            kwargs={'username': self.user_2}
        ))
        self.authorized_client_1.get(reverse(
            'profile_unfollow',
            kwargs={'username': self.user_2}
        ))
        follow_exists = Follow.objects.filter(
            user=self.user_1,
            author=self.user_2
        ).exists()
        self.assertFalse(follow_exists)

    def test_follow_index_page_display_followed_author_post(self):
        """В ленте подписок появляются посты соответствующих авторов"""
        kat_post = Post.objects.create(
            text='Сообщение Катамаранова',
            pub_date='2019-12-19',
            author=self.user_2,
            group=self.ok_group,
        )
        # 'Katamaranov' подписан на 'Polzovatel'
        self.authorized_client_2.get(reverse(
            'profile_follow',
            kwargs={'username': self.user_1}
        ))
        # Пост автора 'Polzovatel' появляется в ленте подписок у 'Katamaranov'
        response = self.authorized_client_2.get(reverse('follow_index'))
        follow_index_page_view_1 = response.context.get('page')
        self.assertIn(self.test_post, follow_index_page_view_1)

        # 'Polzovatel' НЕ подписан на 'Katamaranov'
        # Пост автора 'Katamaranov' НЕ появится в ленте подписок у 'Polzovatel'
        response = self.authorized_client_1.get(reverse('follow_index'))
        follow_index_page_view_2 = response.context.get('page')
        self.assertNotIn(kat_post, follow_index_page_view_2)
    
