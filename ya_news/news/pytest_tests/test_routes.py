from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'name',
    (lf('comment_edit_url'), lf('comment_delete_url')),
)
def test_comment_delete_edit_availability_for_anonymous_user(
        client, name, login_url
):
    """При попытке перейти на страницу редактирования или удаления комментария
    анонимный пользователь перенаправляется на страницу авторизации.
    """
    login_url = login_url
    url = name
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    'reverse_url, parametrized_client, status',
    (
        (
            lf('homepage_url'),
            lf('client'),
            HTTPStatus.OK
        ),
        (
            lf('news_detail_url'),
            lf('client'),
            HTTPStatus.OK
        ),
        (
            lf('signup_url'),
            lf('client'),
            HTTPStatus.OK
        ),
        (
            lf('login_url'),
            lf('client'),
            HTTPStatus.OK
        ),
        (
            lf('logout_url'),
            lf('client'),
            HTTPStatus.OK
        ),
        (
            lf('comment_edit_url'),
            lf('not_author_client'),
            HTTPStatus.NOT_FOUND
        ),
        (
            lf('comment_edit_url'),
            lf('author_client'),
            HTTPStatus.OK
        ),
        (
            lf('comment_delete_url'),
            lf('not_author_client'),
            HTTPStatus.NOT_FOUND
        ),
        (
            lf('comment_delete_url'),
            lf('author_client'),
            HTTPStatus.OK
        ),
    )
)
def test_authorization_statuses_for_different_users(
    reverse_url, parametrized_client, status
):
    response = parametrized_client.get(reverse_url)
    assert response.status_code == status
