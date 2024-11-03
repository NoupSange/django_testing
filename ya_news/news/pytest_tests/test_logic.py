from http import HTTPStatus

import pytest
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


def test_user_cant_create_comment(client, news_detail_url, login_url):
    """Анонимный пользователь не может отправить комментарий."""
    comments_count = Comment.objects.count()
    form_data = {'text': 'Новый текст'}
    login_url = login_url
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
    count_comments = Comment.objects.count()
    url = comment_delete_url
    expected_redirect_url = news_detail_url
    response = author_client.delete(url)
    assertRedirects(response, f'{expected_redirect_url}#comments')
    count_comments_after_delete = Comment.objects.count()
    assert count_comments_after_delete == count_comments - 1


def test_not_author_cant_delete_comment(
        not_author_client, comment_delete_url
):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    count_comments = Comment.objects.count()
    url = comment_delete_url
    response = not_author_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count_after = Comment.objects.count()
    assert count_comments == comments_count_after


def test_author_can_edit_comment(
        author_client, comment, news_detail_url, comment_edit_url
):
    """Авторизованный пользователь может редактировать свои комментарии."""
    edit_url = comment_edit_url
    initial_comment = comment
    form_data = {'text': 'Новый текст'}
    response = author_client.post(edit_url, form_data)
    assertRedirects(response, f'{news_detail_url}#comments')
    comment = Comment.objects.get(pk=comment.pk)
    assert comment.text == form_data['text']
    assert comment.author == initial_comment.author
    assert comment.news == initial_comment.news


def test_not_author_cant_edit_comment(
        not_author_client, comment, comment_edit_url
):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    initial_comment = comment
    edit_url = comment_edit_url
    form_data = {'text': 'Новый текст'}
    response = not_author_client.post(edit_url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment = Comment.objects.get(pk=comment.pk)
    assert comment.text == initial_comment.text
    assert comment.author == initial_comment.author
    assert comment.news == initial_comment.news
