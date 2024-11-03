from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestFixtures(TestCase):

    TITLE = 'Заголовок'
    TEXT = 'Текст'
    SLUG_THE_SAME = 'slug_the_same'

    NEW_TITLE = 'Новый заголовок'
    NEW_TEXT = 'Новый текст'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)

        cls.author_two = User.objects.create(username='Автор заметки 2')

        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.the_same_note_form_data = {
            'title': cls.TITLE,
            'text': cls.TEXT,
            'author': cls.author,
            'slug': cls.SLUG_THE_SAME,
        }
        cls.the_same_note = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            author=cls.author,
            slug=cls.SLUG_THE_SAME,
        )

        cls.new_form_data = {
            'title': cls.NEW_TITLE,
            'text': cls.NEW_TEXT,
        }

        cls.the_authors_note = Note.objects.create(
            title='authors_note',
            text='text_authors_note',
            author=cls.author,
            slug='slug_the_authors_note',
        )
        cls.the_wrong_note = Note.objects.create(
            title='Заголовок_the_wrong_note',
            text='Текст_the_wrong_note',
            author=cls.author_two,
            slug='slug_the_wrong_note',
        )

        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.the_same_note.slug,))
        cls.delete_url = reverse(
            'notes:delete', args=(cls.the_same_note.slug,)
        )
        cls.detail_url = reverse(
            'notes:detail', args=(cls.the_same_note.slug,)
        )
        cls.success_url = reverse('notes:success')
        cls.homepage_url = reverse('notes:home')
        cls.list_url = reverse('notes:list')
