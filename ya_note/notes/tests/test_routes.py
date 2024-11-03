from http import HTTPStatus

from notes.tests.fixtures import TestFixtures


class TestRoutes(TestFixtures):

    def test_home_page(self):
        """Главная страница доступна анонимному пользователю."""
        response = self.client.get(self.homepage_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_user_pages_availability(self):
        """Аутентифицированному пользователю доступна
        страница со списком заметок,
        страница успешного добавления заметки,
        страница добавления новой заметки.
        """
        for name in (self.list_url, self.success_url, self.add_url):
            with self.subTest(user=self.reader):
                url = name
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_pages_availability(self):
        """Страницы отдельной заметки, удаления и редактирования заметки
        доступны только автору заметки. Если на эти страницы попытается
        зайти другой пользователь — вернётся ошибка 404.
        """
        users_statuses = (
            (self.auth_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            for name in (
                (self.detail_url),
                (self.delete_url),
                (self.edit_url),
            ):
                with self.subTest(user=user):
                    url = name
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """При попытке перейти на страницу списка заметок, страницу успешного
        добавления записи, страницу добавления заметки, отдельной заметки,
        редактирования или удаления заметки анонимный пользователь
        перенаправляется на страницу логина.
        """
        login_url = self.login_url
        for name in (
            (self.list_url),
            (self.success_url),
            (self.add_url),
            (self.detail_url),
            (self.edit_url),
            (self.delete_url),
        ):
            with self.subTest(name=name):
                url = name
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_authorization_pages(self):
        """Страницы регистрации пользователей, входа в учётную
        запись и выхода из неё доступны всем пользователям.
        """
        users_statuses = (
            (self.auth_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.OK),
            (self.client, HTTPStatus.OK)
        )
        for name in (
            (self.login_url),
            (self.logout_url),
            (self.signup_url),
        ):
            with self.subTest(name=name):
                for user, status in users_statuses:
                    url = name
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)
