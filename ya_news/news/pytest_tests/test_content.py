# test_content.py
import pytest

from django.urls import reverse
from notes.forms import NoteForm


# В тесте используем фикстуру заметки
# и фикстуру клиента с автором заметки.
@pytest.mark.parametrize(
    'parametrized_client, note_in_list',
    (
    (pytest.lazy_fixture('author_client'), True),
    (pytest.lazy_fixture('not_author_client'), False),
    )
)
def test_notes_list_for_different_users(
        # Используем фикстуру заметки и параметры из декоратора:
            note, parametrized_client, note_in_list
):
        url = reverse('notes:list')
        # Выполняем запрос от имени параметризованного клиента:
        response = parametrized_client.get(url)
        object_list = response.context['object_list']
        # Проверяем истинность утверждения "заметка есть в списке":
        assert (note in object_list) is note_in_list
  

@pytest.mark.parametrize(
    # В качестве параметров передаём name и args для reverse.
    'name, args',
    (
        # Для тестирования страницы создания заметки 
        # никакие дополнительные аргументы для reverse() не нужны.
        ('notes:add', None),
        # Для тестирования страницы редактирования заметки нужен slug заметки.
        ('notes:edit', pytest.lazy_fixture('slug_for_args'))
    )
)
def test_create_note_page_contains_form(
     author_client, name, args):
    url = reverse(name, args=args)
    # Запрашиваем страницу создания заметки:
    response = author_client.get(url)
    # Проверяем, есть ли объект form в словаре контекста:
    assert 'form' in response.context
    # Проверяем, что объект формы относится к нужному классу.
    assert isinstance(response.context['form'], NoteForm)


def test_edit_note_page_contains_form(slug_for_args, author_client):
    url = reverse('notes:edit', args=slug_for_args)
    # Запрашиваем страницу редактирования заметки:
    response = author_client.get(url)
    # Проверяем, есть ли объект form в словаре контекста:
    assert 'form' in response.context
    # Проверяем, что объект формы относится к нужному классу.
    assert isinstance(response.context['form'], NoteForm) 