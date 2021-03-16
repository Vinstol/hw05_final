from django.contrib.auth import get_user_model

from django.test import Client
from django.test import TestCase

from posts.models import Group
from posts.models import Post

START_PAGE = '/'
NEW_POST_PAGE = '/new/'
ABOUT_AUTHOR_PAGE = '/about/author/'
ABOUT_TECH_PAGE = '/about/tech/'


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()


class StaticURLTests(TestCase):
    def setUp(self):
        """Создание экземпляра неавторизованного клиента."""
        self.guest_client = Client()

    def test_homepage(self):
        """Проверка доступности стартовой страницы
        для неавторизованного клиента."""
        response = self.guest_client.get(START_PAGE)
        self.assertEqual(response.status_code, 200, 'Сайт "дымит"!')

    def test_about_url_uses_correct_template(self):
        """Проверка шаблона для стартовой страницы."""
        response = self.guest_client.get(START_PAGE)
        self.assertTemplateUsed(response, 'index.html')


class PostModelTest(TestCase):
    ''' Тестирование модели Post'''
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        User = get_user_model()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Тестовое сообщение!!!',
            pub_date='2011-05-11',
            author=User.objects.create(username='Polzovatel'),
            group=cls.group,
        )

    def setUp(self):
        """ Создание неавторизованного клиента и
        клиента с авторизованным пользователем"""
        self.guest_client = Client()

        user_1 = get_user_model()
        self.user_1 = user_1.objects.get(username='Polzovatel')
        self.authorized_client_1 = Client()
        self.authorized_client_1.force_login(self.user_1)

        user = get_user_model()
        self.user = user.objects.create(username='Katamaranov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.group_page = '/group/{0}/'.format(self.group.slug)
        self.profile_page = '/{0}/'.format(self.post.author)
        self.post_view_page = '/{0}/{1}/'.format(
            self.post.author,
            self.post.id
        )
        self.post_edit_page = '/{0}/{1}/edit/'.format(
            self.post.author,
            self.post.id
        )
        self.comment_page = '/{0}/{1}/comment/'.format(
            self.post.author,
            self.post.id
        )
        self.profle_follow_button = '/{0}/follow/'.format(
            self.post.author
        )
        self.profle_unfollow_button = '/{0}/unfollow/'.format(
            self.post.author
        )

    # Проверяем общедоступные страницы
    def test_index_url_exists_at_desired_location_anonymous(self):
        """Стартовая страница (/) доступна любому пользователю."""
        response = self.guest_client.get(START_PAGE)
        self.assertEqual(response.status_code, 200)

    def test_group_slug_url_exists_at_desired_location_anonymous(self):
        """Страница группы (group/test-slug/) доступна любому пользователю."""
        response = self.guest_client.get(self.group_page)
        self.assertEqual(response.status_code, 200)

    def test_user_profile_url_exists_at_desired_location_anonymous(self):
        """Страница профиля (username/) доступна любому пользователю."""
        response = self.guest_client.get(self.profile_page)
        self.assertEqual(response.status_code, 200)
        response = self.authorized_client_1.get(self.profile_page)
        self.assertEqual(response.status_code, 200)

    def test_post_view_url_exists_at_desired_location_anonymous(self):
        """Страница поста (username/post_id/) доступна любому пользователю."""
        response = self.guest_client.get(self.post_view_page)
        self.assertEqual(response.status_code, 200)
        response = self.authorized_client_1.get(self.post_view_page)
        self.assertEqual(response.status_code, 200)

    def test_about_author_url_exists_at_desired_location_anonymous(self):
        """Страница об авторе (about/author/) доступна любому пользователю."""
        response = self.guest_client.get(ABOUT_AUTHOR_PAGE)
        self.assertEqual(response.status_code, 200)

    def test_about_tech_url_exists_at_desired_location_anonymous(self):
        """Страница о технологиях (about/tech/) доступна любому пользователю"""
        response = self.guest_client.get(ABOUT_TECH_PAGE)
        self.assertEqual(response.status_code, 200)

    def test_404_url_exists_at_desired_location_anonymous(self):
        """Страница с ошибкой 404 (404/) доступна любому пользователю"""
        response = self.guest_client.get('/8888/')
        self.assertEqual(response.status_code, 404)

    # Проверяем доступность страниц для авторизованного пользователя
    def test_url_new_exists_at_desired_location_logged_user(self):
        """Страница /new/ доступна авторизованному пользователю."""
        response = self.authorized_client.get(NEW_POST_PAGE)
        self.assertEqual(response.status_code, 200)

    def test_url_add_comment_exists_at_desired_location_logged_user(self):
        """Страница созд. комментария доступна авторизованному пользователю."""
        response = self.authorized_client.get(self.comment_page)
        self.assertEqual(response.status_code, 200)

    # Проверяем редиректы для неавторизованного пользователя
    def test_url_new_redirect_anonymous_on_login(self):
        """Страница создания нового поста (/new/) перенаправит
        анонимного пользователя на страницу логина."""
        response = self.client.get(NEW_POST_PAGE, follow=True)
        self.assertRedirects(
            response, ('/auth/login/?next=/new/'))

    def test_post_edit_url_redirect_anonymous_on_login(self):
        """Страница редактирования поста (username/post_id/edit/)
        перенаправит анонимного пользователя на страницу логина."""
        response = self.client.get(self.post_edit_page, follow=True)
        self.assertRedirects(
            response,
            ('/auth/login/?next=/{0}/{1}/edit/'.format(
                self.post.author,
                self.post.id
            ))
        )

    def test_comment_url_redirect_anonymous_on_login(self):
        """Страница создания комментария поста (username/post_id/comment/)
        перенаправит анонимного пользователя на страницу логина."""
        response = self.client.get(self.comment_page, follow=True)
        self.assertRedirects(
            response,
            ('/auth/login/?next=/{0}/{1}/comment/'.format(
                self.post.author,
                self.post.id
            ))
        )

    def test_profile_follow_url_redirect_anonymous_on_login(self):
        """Кнопка «Подписаться» (username/post_id/comment/)
        перенаправит анонимного пользователя на страницу логина."""
        response = self.client.get(self.profle_follow_button, follow=True)
        self.assertRedirects(
            response,
            ('/auth/login/?next=/{0}/follow/'.format(self.post.author))
        )
    
    def test_profile_unfollow_url_redirect_anonymous_on_login(self):
        """Кнопка «Отписаться» (username/post_id/comment/)
        перенаправит анонимного пользователя на страницу логина."""
        response = self.client.get(self.profle_unfollow_button, follow=True)
        self.assertRedirects(
            response,
            ('/auth/login/?next=/{0}/unfollow/'.format(self.post.author))
        )

    # Проверяем редирект для авторизованного пользователя, не автора поста
    def test_post_edit_url_redirect_not_author_on_post_view(self):
        """Страница редактирования поста (username/post_id/edit/)
        перенаправит не автора поста на страницу просмотра поста."""
        response = self.authorized_client.get(self.post_edit_page, follow=True)
        self.assertRedirects(
            response,
            ('/{0}/{1}/'.format(self.post.author, self.post.id))
        )

    # Проверка корректности вызываемых шаблонов для каждого адреса
    def test_urls_uses_correct_template(self):
        """Проверка использования URL-адресом соответствующего HTML-шаблона."""
        templates_url_names = {
            'index.html': START_PAGE,
            'group.html': self.group_page,
            'new_post.html': NEW_POST_PAGE,
            'profile.html': self.profile_page,
            'post.html': self.post_view_page,
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    # Проверка доступности страницы редактирования поста разным пользователям
    def test_post_edit_url_exists_at_desired_location_anonymous(self):
        """Страница редактирования поста НЕ доступна гостю."""
        response = self.guest_client.get(self.post_edit_page)
        self.assertEqual(response.status_code, 302)

    def test_post_edit_url_exists_at_desired_location_not_author(self):
        """Страница редактирования поста НЕ доступна НЕ автору поста"""
        response = self.authorized_client.get(self.post_edit_page)
        self.assertEqual(response.status_code, 302)

    def test_post_edit_url_exists_at_desired_location_author(self):
        """Страница редактирования поста доступна только автору поста"""
        response = self.authorized_client_1.get(self.post_edit_page)
        self.assertEqual(response.status_code, 200)
