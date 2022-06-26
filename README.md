# Yandex Enrollment

## Что использовано

Писал я данный сервис с использованием фреймворков [FastApi](https://fastapi.tiangolo.com/) и [SQLAlchemy](https://www.sqlalchemy.org).
Использовал FastApi, так как этот фреймворк имеет интеграцию с [pydantic](https://pydantic-docs.helpmanual.io/), что позволило потратить меньше времени на
вопросы валидации данных, приходящих от клиентов. Также FastApi из коробки предоставляет возможность использования асинхронности, что так же положительно
сказалось на производительности сервиса.

## Что выполнено

Я реализовал 4 HTTP ручки из 5 предложенных:
- `POST /imports`
- `DELETE /delete`
- `GET /nodes`
- `GET /sales`

посмотреть документацию по этим ручкам можно и спецификацию моделей можно [здесь](https://favorites-1937.usr.yandex-academy.ru/docs#/).

## Как запустить

Клонируем данный репозиторий:

```bash
git clone https://github.com/dkharms/yandex-enrollment.git
```

Далее есть несколько способов запуска:

1. Чистый `python` без виртуального окружения:
```bash
pip install -r requirements.txt && sudo sh run-server.sh PROD
```

2. Запуск с ипользованием `Docker`:
```bash
docker build --tag "dkharms/docker-private:yandex-enrollment"
```
```bash
docker run --rm --name yandex-enrollment \
    -v /usr/local/yandex:/app/instances \
    -v /usr/local/yandex:/app/logs \
    -p 80:80 \
    dkharms/docker-private:yandex-enrollment
```

Проверяем жизнеспособность сервиса:
```bash
curl localhost/ping
```
если приходит `HTTP 200`, то сервис готов к использованию.

## Генерация данных

Можно использовать скрипт `generator.py`, чтобы сгенерировать валидные данные для ручки `/imports`.

## Покрытие тестами

```bash
python -m pytest -rA --cov=app --cov-report term app/test
```
<img width="1458" alt="image" src="https://user-images.githubusercontent.com/29202384/175809977-a798fe86-78f2-4720-b7d9-2d05e31f1854.png">

