from http import HTTPStatus
import pytest

from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_user_can_create_comment(author_client, form_data, news):
    """Авторизованный пользователь может отправить комментарий."""
    url = reverse('news:detail', args=(news.pk,))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']


@pytest.mark.django_db
def test_user_cant_create_comment(client, form_data, news):
    """Анонимный пользователь не может отправить комментарий."""
    login_url = reverse('users:login')
    url = reverse('news:detail', args=(news.pk, ))
    expected_url = f'{login_url}?next={url}'
    response = client.post(url, data=form_data)
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_cant_use_bad_words(author_client, news):
    """Если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=(news.pk, ))
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, news, comment):
    """Авторизованный пользователь может
    редактировать или удалять свои комментарии.
    """
    url = reverse('news:delete', args=(comment.pk,))
    expected_redirect_url = reverse('news:detail', args=(news.pk,))
    response = author_client.delete(url)
    assertRedirects(response, f'{expected_redirect_url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_not_author_cant_delete_comment(not_author_client, comment):
    """Авторизованный пользователь не может
    редактироватьили удалять чужие комментарии.
    """
    url = reverse('news:delete', args=(comment.pk,))
    response = not_author_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1
