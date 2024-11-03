from django.contrib.auth import get_user_model

from notes.forms import NoteForm
from notes.tests.fixtures import TestFixtures

User = get_user_model()


class TestContent(TestFixtures):

    def test_note_present_in_notelist(self):
        """Отдельная заметка передаётся на страницу со
        списком заметок в списке object_list в словаре context
        """
        response = self.auth_client.get(self.NOTES_LIST_URL)
        notes_feed = response.context['notes_feed']
        self.assertIn(self.the_authors_note, notes_feed)

    def test_notelist_is_visible_only_to_author(self):
        """В список заметок одного пользователя не
        попадают заметки другого пользователя
        """
        response = self.auth_client.get(self.NOTES_LIST_URL)
        notes_feed = response.context['notes_feed']
        self.assertNotIn(self.the_wrong_note, notes_feed)

    def test_add_edit_form_presence(self):
        """На страницы создания и редактирования заметки передаются формы."""
        urls = (
            self.add_url,
            self.edit_url
        )
        for name in urls:
            with self.subTest(name=name):
                url = name
                response = self.auth_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
