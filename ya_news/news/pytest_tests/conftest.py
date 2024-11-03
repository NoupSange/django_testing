from datetime import date, timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News

today = date.today()


@pytest.fixture
def author(django_user_model):
    """Автор новостей и комментариев."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    """Читатель."""
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    """Авторизованный автор."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    """Авторизованный читатель."""
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news(author):
    """Новость автора."""
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки',
        date=today
    )
    return news


@pytest.fixture
def comment(author, news):
    """Комментарий автора."""
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='text',
    )
    return comment


@pytest.fixture
def create_news():
    """Набор новостей автора."""
    News.objects.bulk_create(
        News(title=f'Новость {index}',
             text='Просто текст.',
             date=today - timedelta(days=index))
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def create_comments(news, author):
    """Набор комментариев автора."""
    now = timezone.now()
    for index in range(5):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def homepage_url():
    url = reverse('news:home')
    return url


@pytest.fixture
def news_detail_url(news):
    url = reverse('news:detail', args=(news.pk,))
    return url


@pytest.fixture
def comment_delete_url(comment):
    url = reverse('news:delete', args=(comment.pk,))
    return url


@pytest.fixture
def comment_edit_url(comment):
    url = reverse('news:edit', args=(comment.pk,))
    return url


@pytest.fixture
def login_url():
    url = reverse('users:login')
    return url


@pytest.fixture
def logout_url():
    url = reverse('users:logout')
    return url


@pytest.fixture
def signup_url():
    url = reverse('users:signup')
    return url
