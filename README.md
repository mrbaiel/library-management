# Library Management Backend

REST API для управления библиотекой: книги, авторы, избранное, периодические задачи.

## Стек

- Python 3.12+ / Django 5 / DRF
- PostgreSQL
- JWT (simplejwt)
- Celery + Redis
- Swagger (drf-spectacular)
- Docker

## Установка

    git clone 

## Запуск

    docker-compose up --build

    Сервисы :
      - API :
        http://localhost:8000/admin/
        http://localhost:8000/api/

      для создания суперпользователя:
        docker-compose exec web uv run python manage.py createsuperuser

## API документация

После запуска проекта:

- Swagger UI — http://localhost:8000/api
- ReDoc — http://localhost:8000/api/redoc/
- OpenAPI schema (JSON) — http://localhost:8000/api/schema/

Для авторизации нажми **Authorize** и вставьте `Bearer <access_token>`, access_token берется из `POST /api/auth/login/`

## Эндпоинты

| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/api/auth/register/` | Регистрация |
| POST | `/api/auth/login/` | Получить JWT |
| POST | `/api/auth/logout/` | Логаут (blacklist refresh) |
| POST | `/api/auth/refresh/` | Обновить access |
| GET POST | `/api/authors/` | Список / создать автора |
| GET PUT DELETE | `/api/authors/{id}/` | Детально / редактировать / удалить |
| GET POST | `/api/books/` | Список / создать книгу |
| GET PUT DELETE | `/api/books/{id}/` | Детально / редактировать / удалить |
| GET POST | `/api/favorites/` | Свой список / добавить |
| DELETE | `/api/favorites/{id}/` | Удалить запись из избранного |
| DELETE | `/api/favorites/clear/` | Очистить весь список |


## Фильтрация, поиск, сортировка

- Фильтры: `?genre=роман`, `?authors=1`, `?publication_date=1869-01-01`
- Поиск: `?search=толстой` (по названию книги и фамилии автора)
- Сортировка: `?ordering=publication_date`, `?ordering=-publication_date`,
  `?ordering=authors__last_name`, `?ordering=genre`

## Периодические задачи (Celery)

- `notify_new_books` — раз в день рассылает email со списком книг
  добавленных за последние 24 часа.
- `notify_anniversary_books` — проверяет книги с датой публикации
  5, 10 или 20 лет назад и шлёт уведомление пользователям

Расписание настраивается через админку: **Periodic Tasks → Periodic tasks**

## ER диаграмма

<img width="2068" height="1077" alt="image" src="https://github.com/user-attachments/assets/c774b259-8744-4176-ab71-f0e0ec0704b4" />


## Тесты

    docker-compose exec web uv run python manage.py test