
from datetime import date, timedelta
import pytest

from django.conf import settings
from django.test.client import Client
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
    """10 новостей автора"""
    all_news = News.objects.bulk_create(
        News(title=f'Новость {index}',
             text='Просто текст.',
             date=today - timedelta(days=index))
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )
    return all_news


@pytest.fixture
def create_comments(news, author):
    """5 комментариев автора"""
    now = timezone.now()
    for index in range(5):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст',
    }
