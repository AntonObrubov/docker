# Todo-приложение на Flask + PostgreSQL

## Запуск

```bash
docker-compose up --build
```

## API

GET /tasks – получить все задачи

POST /tasks – создать задачу (JSON: {"title": "..."})

PUT /tasks/<id> – обновить задачу (JSON: {"done": true} или {"title": "..."})

DELETE /tasks/<id> – удалить задачу

## Доступ

После запуска приложение доступно по адресу http://localhost:8080