from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Создание фикстур автора заметки и просто
        аутентифицированного пользователя, объекта заметки
        """
        cls.author = User.objects.create(username='Автор заметки')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заголовок', text='Текст', author=cls.author
        )

    def test_home_page(self):
        """Главная страница доступна анонимному пользователю."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_user_pages_availability(self):
        """Аутентифицированному пользователю доступна
        страница со списком заметок,
        страница успешного добавления заметки,
        страница добавления новой заметки.
        """
        self.client.force_login(self.reader)
        for name in ('notes:list', 'notes:success', 'notes:add'):
            with self.subTest(user=self.reader):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_pages_availability(self):
        """Страницы отдельной заметки, удаления и редактирования заметки
        доступны только автору заметки. Если на эти страницы попытается
        зайти другой пользователь — вернётся ошибка 404.
        """
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name, args in (
                ('notes:detail', (self.note.slug,)),
                ('notes:delete', (self.note.slug,)),
                ('notes:edit', (self.note.slug,)),
            ):
                with self.subTest(user=user):
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """При попытке перейти на страницу списка заметок, страницу успешного
        добавления записи, страницу добавления заметки, отдельной заметки,
        редактирования или удаления заметки анонимный пользователь
        перенаправляется на страницу логина.
        """
        login_url = reverse('users:login')
        for name, args in (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        ):
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_authorization_pages(self):
        """Страницы регистрации пользователей, входа в учётную
        запись и выхода из неё доступны всем пользователям.
        """
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.OK),
            (None, HTTPStatus.OK)
        )
        for name in (
            ('users:login'),
            ('users:logout'),
            ('users:signup'),
        ):
            with self.subTest(name=name):
                for user, status in users_statuses:
                    if user is not None:
                        self.client.force_login(user)
                    else:
                        pass
                    url = reverse(name)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)
