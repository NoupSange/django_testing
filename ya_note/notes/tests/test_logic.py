# news/tests/test_logic.py
from http import HTTPStatus
from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()

TITLE = 'Заголовок'
TEXT = 'Текст'
SLUG_THE_SAME = 'slug_the_same'

NEW_TITLE = 'Новый заголовок'
NEW_TEXT = 'Новый текст'


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.url = reverse('notes:add')
        cls.form_data = {
            'title': TITLE,
            'text': TEXT,
            'author': cls.author,
            'slug': SLUG_THE_SAME,
        }

    def test_create_note(self):
        """Залогиненный пользователь может создать заметку,
        а анонимный — не может.
        """
        users = (
            (self.client, 0),
            (self.auth_client, 1),
        )
        for user, expected_count_result in users:
            with self.subTest(user=user):
                user.post(self.url, data=self.form_data)
                count_result = Note.objects.count()
                self.assertEqual(count_result, expected_count_result)

    def test_cant_create_identical_slug_notes(self):
        """Невозможно создать две заметки с одинаковым slug."""
        Note.objects.create(
            title=TITLE,
            text=TEXT,
            author=self.author,
            slug=SLUG_THE_SAME,
        )
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=SLUG_THE_SAME + WARNING,
        )
        count_result = Note.objects.count()
        self.assertEqual(count_result, 1)

    def test_auto_generate_slug(self):
        """Если при создании заметки не заполнен slug, то он формируется
        автоматически, с помощью функции pytils.translit.slugify.
        """
        note = Note.objects.create(
            title=TITLE,
            text=TEXT,
            author=self.author,
        )
        expected_slug = slugify(TITLE)
        self.assertEqual(note.slug, expected_slug)


class TestNoteEditDelete(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            title=TITLE,
            text=TEXT,
            author=cls.author,
            slug=SLUG_THE_SAME,
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.success_url = reverse('notes:success')

        cls.form_data = {
            'title': NEW_TITLE,
            'text': NEW_TEXT,
        }

    def test_author_can_delete_his_note(self):
        """Пользователь может удалять свои заметки"""
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_comment_of_another_user(self):
        """Пользователь не может удалять чужие заметки."""
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_his_note(self):
        """Пользователь может редактировать свои заметки."""
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, NEW_TEXT)

    def test_user_cant_edit_note_of_another_user(self):
        """Пользователь не может редактировать чужие заметки."""
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, TEXT)
