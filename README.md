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
      - API - http://localhost:8000
        - Swagger :
          - http://localhost:8000/api/docs/
          - http://localhost:8000/api/schema/
          - http://localhost:8000/api/redoc/
    
      для создания суперпользователя:
        docker-compose exec web uv run python manage.py createsuperuser

## API документация

После запуска проекта:

- Swagger UI — http://localhost:5000/api
- ReDoc — http://localhost:5000/api/redoc/
- OpenAPI schema (JSON) — http://localhost:5000/api/schema/

Для авторизации нажми **Authorize** и вставьте `Bearer <access_token>`, access_token берется из `POST /api/auth/login/`

## ER диаграмма

<img width="2068" height="1077" alt="image" src="https://github.com/user-attachments/assets/c774b259-8744-4176-ab71-f0e0ec0704b4" />


## Тесты

    docker-compose exec web uv run python manage.py test