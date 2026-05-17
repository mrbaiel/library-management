from datetime import timedelta
from celery import shared_task
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils import timezone

from .models import Book


@shared_task
def notify_new_books():
    """Раз в день: рассылка книг, добавленных за последние 24 часа."""
    since = timezone.now() - timedelta(days=1)
    new_books = Book.objects.filter(created_at__gte=since)

    if not new_books.exists():
        return 'No new books'

    titles = '\n'.join(f'- {b.title}' for b in new_books)
    message = f'Новые книги за последние 24 часа:\n\n{titles}'

    users = User.objects.filter(is_active=True, email__gt='')
    for user in users:
        send_mail(
            subject='Новые книги в библиотеке',
            message=message,
            from_email='noreply@library.local',
            recipient_list=[user.email],
        )
    return f'Sent to {users.count()} users, {new_books.count()} books'


@shared_task
def notify_anniversary_books():
    """Уведомления о книгах-юбилярах (5, 10, 20 лет назад)."""
    today = timezone.now().date()
    anniversaries = [5, 10, 20]

    for years in anniversaries:
        try:
            past_date = today.replace(year=today.year - years)
        except ValueError:
            # 29 февраля в невисокосный год
            past_date = today.replace(year=today.year - years, day=28)

        books = Book.objects.filter(publication_date=past_date)
        if not books.exists():
            continue

        titles = '\n'.join(f'- {b.title}' for b in books)
        message = f'Книги-юбиляры ({years} лет назад):\n\n{titles}'

        users = User.objects.filter(is_active=True, email__gt='')
        for user in users:
            send_mail(
                subject=f'Юбилей книг — {years} лет',
                message=message,
                from_email='noreply@library.local',
                recipient_list=[user.email],
            )

    return 'Anniversary check complete'