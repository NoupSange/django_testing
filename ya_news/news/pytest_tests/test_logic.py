from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db


def test_user_can_create_comment(author_client, author, news, news_detail_url):
    """Авторизованный пользователь может отправить комментарий."""
    Comment.objects.all().delete()
    form_data = {'text': 'Новый текст', 'author': author, 'news': news}
    url = news_detail_url
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == form_data['author']
    assert new_comment.news == form_data['news']


def test_user_cant_create_comment(client, news_detail_url):
    """Анонимный пользователь не может отправить комментарий."""
    comments_count = Comment.objects.count()
    form_data = {'text': 'Новый текст'}
    login_url = reverse('users:login')
    url = news_detail_url
    expected_url = f'{login_url}?next={url}'
    response = client.post(url, data=form_data)
    assertRedirects(response, expected_url)
    assert comments_count == Comment.objects.count()


def test_user_cant_use_bad_words(author_client, news_detail_url):
    """Если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    comments_count = Comment.objects.count()
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = news_detail_url
    response = author_client.post(url, data=bad_words_data)
    assert comments_count == Comment.objects.count()
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )


def test_author_can_delete_comment(
        author_client, news_detail_url, comment_delete_url
):
    """Авторизованный пользователь может удалять свои комментарии."""
    url = comment_delete_url
    expected_redirect_url = news_detail_url
    response = author_client.delete(url)
    assertRedirects(response, f'{expected_redirect_url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_not_author_cant_delete_comment(
        not_author_client, comment_delete_url
):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    url = comment_delete_url
    response = not_author_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(
        author_client, comment, news_detail_url, comment_edit_url
):
    """Авторизованный пользователь может редактировать свои комментарии."""
    edit_url = comment_edit_url
    form_data = {'text': 'Новый текст'}
    response = author_client.post(edit_url, form_data)
    assertRedirects(response, f'{news_detail_url}#comments')
    comment.refresh_from_db()
    assert comment.text == 'Новый текст'


def test_not_author_cant_edit_comment(
        not_author_client, comment, comment_edit_url
):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    initial_comment_text = comment.text
    edit_url = comment_edit_url
    form_data = {'text': 'Новый текст'}
    response = not_author_client.post(edit_url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == initial_comment_text
