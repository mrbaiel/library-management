from datetime import date, timedelta
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from .models import Author, Book, FavoriteBook
from .tasks import notify_new_books, notify_anniversary_books


class BaseAPITestCase(TestCase):
    """Базовый класс — создаёт юзера и аутентифицирует клиент."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='tester', email='t@t.com', password='pass12345'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)


# ============== МОДЕЛИ ==============

class AuthorModelTest(TestCase):
    def test_create_author(self):
        author = Author.objects.create(
            first_name='Лев', last_name='Толстой',
            date_of_birth=date(1828, 9, 9),
        )
        self.assertEqual(str(author), 'Лев Толстой')
        self.assertIsNone(author.date_of_death)


class BookModelTest(TestCase):
    def test_book_authors_m2m(self):
        a1 = Author.objects.create(first_name='A', last_name='One', date_of_birth=date(1900, 1, 1))
        a2 = Author.objects.create(first_name='B', last_name='Two', date_of_birth=date(1910, 1, 1))
        book = Book.objects.create(
            title='Test', isbn='123', publication_date=date(2000, 1, 1), genre='novel'
        )
        book.authors.set([a1, a2])
        self.assertEqual(book.authors.count(), 2)
        self.assertEqual(str(book), 'Test')


class FavoriteBookModelTest(TestCase):
    def test_unique_together(self):
        user = User.objects.create_user(username='u', password='p')
        book = Book.objects.create(
            title='B', isbn='1', publication_date=date(2000, 1, 1), genre='g'
        )
        FavoriteBook.objects.create(user=user, book=book)
        with self.assertRaises(Exception):
            FavoriteBook.objects.create(user=user, book=book)


# ============== AUTHOR API ==============

class AuthorAPITest(BaseAPITestCase):
    def test_create_author(self):
        data = {'first_name': 'Ф', 'last_name': 'Достоевский', 'date_of_birth': '1821-11-11'}
        res = self.client.post('/api/authors/', data, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Author.objects.count(), 1)

    def test_list_authors(self):
        Author.objects.create(first_name='A', last_name='B', date_of_birth=date(1900, 1, 1))
        res = self.client.get('/api/authors/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_unauthorized(self):
        self.client.force_authenticate(user=None)
        res = self.client.get('/api/authors/')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# ============== BOOK API ==============

class BookAPITest(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.author = Author.objects.create(
            first_name='Лев', last_name='Толстой', date_of_birth=date(1828, 9, 9)
        )

    def test_create_book(self):
        data = {
            'title': 'Война и мир', 'isbn': 'isbn1',
            'authors': [self.author.id],
            'publication_date': '1869-01-01', 'genre': 'роман',
        }
        res = self.client.post('/api/books/', data, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_filter_by_genre(self):
        Book.objects.create(title='B1', isbn='1', publication_date=date(2000, 1, 1), genre='novel')
        Book.objects.create(title='B2', isbn='2', publication_date=date(2000, 1, 1), genre='poetry')
        res = self.client.get('/api/books/?genre=novel')
        self.assertEqual(len(res.data), 1)

    def test_search_by_title(self):
        Book.objects.create(title='Война и мир', isbn='1', publication_date=date(2000, 1, 1), genre='r')
        Book.objects.create(title='Анна Каренина', isbn='2', publication_date=date(2000, 1, 1), genre='r')
        res = self.client.get('/api/books/?search=война')
        self.assertEqual(len(res.data), 1)


# ============== FAVORITES ==============

class FavoriteAPITest(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.book = Book.objects.create(
            title='B', isbn='1', publication_date=date(2000, 1, 1), genre='g'
        )

    def test_add_favorite(self):
        res = self.client.post('/api/favorites/', {'book': self.book.id}, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FavoriteBook.objects.count(), 1)

    def test_list_only_own_favorites(self):
        other = User.objects.create_user(username='other', password='p')
        FavoriteBook.objects.create(user=other, book=self.book)
        FavoriteBook.objects.create(user=self.user, book=self.book)
        res = self.client.get('/api/favorites/')
        self.assertEqual(len(res.data), 1)

    def test_clear_favorites(self):
        FavoriteBook.objects.create(user=self.user, book=self.book)
        res = self.client.delete('/api/favorites/clear/')
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(FavoriteBook.objects.count(), 0)


# ============== CELERY TASKS ==============

class CeleryTasksTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='u', email='u@u.com', password='p'
        )

    @patch('books.tasks.send_mail')
    def test_notify_new_books_sends_mail(self, mock_send):
        Book.objects.create(title='New', isbn='1', publication_date=date(2000, 1, 1), genre='g')
        result = notify_new_books()
        mock_send.assert_called_once()
        self.assertIn('Sent to', result)

    @patch('books.tasks.send_mail')
    def test_notify_new_books_skips_when_empty(self, mock_send):
        # Книга старше 24 часов — не должна попасть
        old = Book.objects.create(title='Old', isbn='2', publication_date=date(2000, 1, 1), genre='g')
        Book.objects.filter(id=old.id).update(created_at=timezone.now() - timedelta(days=2))
        result = notify_new_books()
        mock_send.assert_not_called()
        self.assertEqual(result, 'No new books')

    @patch('books.tasks.send_mail')
    def test_anniversary_task(self, mock_send):
        today = timezone.now().date()
        try:
            anniversary_date = today.replace(year=today.year - 10)
        except ValueError:
            anniversary_date = today.replace(year=today.year - 10, day=28)
        Book.objects.create(
            title='Юбиляр', isbn='1',
            publication_date=anniversary_date, genre='g',
        )
        notify_anniversary_books()
        mock_send.assert_called()