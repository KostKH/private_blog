# private_blog
![yamdb_workflow](https://github.com/KostKH/private_blog/actions/workflows/private_blog_workflow.yml/badge.svg)

private_blog - это проект сайта/персонального блога.
Пример сайта, работающего на данном коде - <a href="https://kostkh.sytes.net">https://kostkh.sytes.net</a>

На данном сайте автор блога размещает свои публикации. А другие посетители сайта могут зарегистрироваться, оставлять лайки и комментарии под статьями. Также посетители могут вести личную переписку с автором блога. Для автора блога создан удобный интерфейс для добавления, изменения и удаления статей и для ведения переписки с читателями блога. 

Проект реализован на MVT-архитектуре с использованием фреймфорка Django. В проекте реализована система регистрации новых посетителей, восстановление паролей через почту, система пользовательских профилей, пагинация статей/комментариев/сообщений и кэширование страниц, механизм комментирования статей. Также реализован механизм обмена сообщениями между читателями и автором блога. Проект имеет верстку с адаптацией под размер экрана устройства пользователя.

## Системные требования
- Python 3.10+
- Works on Linux, Windows, macOS

## Технологии:
- Python 3.10
- Django 4.1.1
- PostgreSQL
- Bootstrap 5.0
- Nginx 1.23.0

## Как запустить проект:

Для запуска проекта на локальной машине с целью дальнейшей кастомизации шаблонов под свои нужды в проект вложены development-версии конфигураций Nginx и docker-compose. После запуска docker-compose сайт будет доступен по адресу: http://127.0.0.1/

Необходимо выполнить следующие шаги:
- Клонировать репозиторий и перейти в папку проекта, где расположен файл manage.py:
```
git clone https://github.com/KostKH/private_blog.git
cd private_blog/private_blog/
```
- Проверить, что свободны порты, необходимые для работы приложения: порт 8000 (требуется для работы приложения) и порт 5432 (требуется для работы  Postgres)

- Проверить, что на машине установлены docker и docker-compose 

- Сгенерировать свой секретный ключ для Django:
```
python manage.py shell
from django.core.management.utils import get_random_secret_key
get_random_secret_key()
exit()
```
- перейти в папку infra_dev, в которой лежат конфигурации docker-compose и nginx:
```
cd ../infra_dev
```
- Cоздать в папке infra_dev файл .env с переменными окружения:
```
touch .env
```
- Заполнить .env файл переменными окружения.Пример:
```
echo SECRET_KEY=***укажите здесь вместо зведочек и этого текста сгенерированный вами секретный ключ *** >>.env
echo DB_ENGINE=django.db.backends.postgresql >>.env
echo DB_NAME=postgres >>.env
echo POSTGRES_USER=postgres >>.env
echo POSTGRES_PASSWORD=***укажите здесь вместо зведочек и этого текста пароль для Postgres*** >>.env
echo DB_HOST=db >>.env
echo DB_PORT=5432 >>.env
echo EMAIL_HOST=***укажите здесь вместо зведочек и этого текста smtp-сервер почты*** >> .env
echo EMAIL_HOST_USER=***укажите здесь вместо зведочек и этого текста почтовый ящик*** >> .env
echo EMAIL_HOST_PASSWORD=***укажите здесь вместо зведочек и этого текста пароль для почтового ящика*** >> .env
echo DEFAULT_FROM_EMAIL=***укажите здесь вместо зведочек и этого текста почтовый ящик*** >> .env
echo EMAIL_PORT=***укажите здесь вместо зведочек и этого текста порт - возможно это будет 587*** >> .env
echo EMAIL_USE_TLS=True >> .env
echo CSRF_TRUSTED_ORIGINS=http://127.0.0.1 >> .env

```
- Установить и запустить приложения в контейнерах:
```
docker-compose up -d
```
- Запустить миграции, создать суперюзера, собрать статику и заполнить БД:
```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --no-input
```
## О программе:

Лицензия: BSD 3-Clause License

Автор: Константин Харьков