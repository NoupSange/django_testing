from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    NOTES_LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author_one = User.objects.create(username='Автор заметки 1')
        cls.author_two = User.objects.create(username='Автор заметки 2')
        author_one_notes = [
            Note(
                title=f'Заголовок{index}',
                text='Текст',
                author=cls.author_one,
                slug=f'slug_1{index}',
            )
            for index in range(5)
        ]
        author_two_notes = [
            Note(
                title=f'Заголовок{index}',
                text='Текст',
                author=cls.author_two,
                slug=f'slug_2{index}',
            )
            for index in range(5)
        ]
        Note.objects.bulk_create(author_one_notes)
        Note.objects.bulk_create(author_two_notes)

        cls.the_authors_note = Note.objects.create(
            title='Заголовок_the_note',
            text='Текст',
            author=cls.author_one,
            slug='slug_the_note',
        )
        cls.the_wrong_note = Note.objects.create(
            title='Заголовок_the_wrong_note',
            text='Текст',
            author=cls.author_two,
            slug='slug_the_wrong_note',
        )

    def test_note_present_in_notelist(self):
        """Отдельная заметка передаётся на страницу со
        списком заметок в списке object_list в словаре context
        """
        self.client.force_login(self.author_one)

        response = self.client.get(self.NOTES_LIST_URL)
        object_list = response.context['notes_feed']
        self.assertIn(self.the_authors_note, object_list)

    def test_notelist_is_visible_only_to_author(self):
        """В список заметок одного пользователя не
        попадают заметки другого пользователя
        """
        self.client.force_login(self.author_one)
        response = self.client.get(self.NOTES_LIST_URL)
        object_list = response.context['notes_feed']
        self.assertNotIn(self.the_wrong_note, object_list)

    def test_add_edit_form_presence(self):
        """На страницы создания и редактирования заметки передаются формы."""
        self.client.force_login(self.author_one)
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.the_authors_note.slug,))
        )
        for name, args in urls:
            url = reverse(name, args=args)
            response = self.client.get(url)
            self.assertIn('form', response.context)
            self.assertIsInstance(response.context['form'], NoteForm)
