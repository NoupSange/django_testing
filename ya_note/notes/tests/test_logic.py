from http import HTTPStatus

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from notes.tests.fixtures import TestFixtures


class TestNoteCreation(TestFixtures):

    def test_create_note(self):
        """Залогиненный пользователь может создать заметку,
        а анонимный — не может.
        """
        users = (
            (self.client, 0),
            (self.auth_client, 1),
        )
        for user, note in users:
            with self.subTest(user=user):
                url = self.add_url
                count_notes = Note.objects.count()
                post_data = {
                    'title': 'create_note_title',
                    'text': 'create_note_text',
                    'slug': 'create_note_slug',
                }
                user.post(url, post_data)
                count_result = Note.objects.count()
                self.assertEqual(count_result, count_notes + note)
                if user == self.auth_client:
                    note = Note.objects.get(slug=post_data['slug'])
                    assert note.title == post_data['title']
                    assert note.text == post_data['text']

    def test_cant_create_identical_slug_notes(self):
        """Невозможно создать две заметки с одинаковым slug."""
        count_notes = Note.objects.count()
        response = self.auth_client.post(
            self.add_url, data=self.the_same_note_form_data
        )
        count_result = Note.objects.count()
        self.assertEqual(count_result, count_notes)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=self.SLUG_THE_SAME + WARNING,
        )

    def test_auto_generate_slug(self):
        """Если при создании заметки не заполнен slug, то он формируется
        автоматически, с помощью функции pytils.translit.slugify.
        """
        url = self.add_url
        Note.objects.all().delete()
        self.auth_client.post(url, data={
            'title': self.TITLE,
            'text': self.TEXT,
        })
        note = Note.objects.get()
        result_slug = note.slug
        expected_slug = slugify(self.TITLE)
        self.assertEqual(result_slug, expected_slug)


class TestNoteEditDelete(TestFixtures):

    def test_author_can_delete_his_note(self):
        """Пользователь может удалять свои заметки"""
        count_notes = Note.objects.count()
        response = self.auth_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        count_notes_after_delete = Note.objects.count()
        self.assertEqual(count_notes - 1, count_notes_after_delete)

    def test_user_cant_delete_comment_of_another_user(self):
        """Пользователь не может удалять чужие заметки."""
        count_notes = Note.objects.count()
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        count_notes_after_delete = Note.objects.count()
        self.assertEqual(count_notes, count_notes_after_delete)

    def test_author_can_edit_his_note(self):
        """Пользователь может редактировать свои заметки."""
        response = self.auth_client.post(
            self.edit_url, data=self.new_form_data
        )
        self.assertRedirects(response, self.success_url)
        note = Note.objects.get(pk=self.the_same_note.pk)
        self.assertEqual(note.text, self.new_form_data['text'])
        self.assertEqual(note.title, self.new_form_data['title'])
        self.assertEqual(note.author, self.the_same_note.author)

    def test_user_cant_edit_note_of_another_user(self):
        """Пользователь не может редактировать чужие заметки."""
        response = self.reader_client.post(
            self.edit_url, data=self.new_form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note = Note.objects.get(pk=self.the_same_note.pk)
        self.assertEqual(note.text, self.the_same_note.text)
        self.assertEqual(note.title, self.the_same_note.title)
        self.assertEqual(note.author, self.the_same_note.author)
        self.assertEqual(note.slug, self.the_same_note.slug)
