## Описание
Это проект Foodgram — «Продуктовый помощник». На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в избранное, а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

**Фронтенд был предоставлен Яндекс.практикумом.**

## Использованные технологии
- django2
- djangorestframework
- python3

## Как запустить проект
Заполните файл infra/.env следующими данными.

```
SECRET_KEY=yoursecretkey
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=userpassword
DB_HOST=db
DB_PORT=5432
```

При необходимости поменяйте значения на желаемые.

Выполните `docker-compose up -d`

Проект готов к использованию.

Для наполнения базы готовым набором ингредиентов из приложенного json-файла используйте команду `docker-compose exec -T web python manage.py loaddata --format json - < ../data/ingredients.json`

Чтобы создать пользователя с правами администратора, выполните `docker-compose exec web python manage.py createsuperuser` и укажите требуемые данные.

Секретный ключ можно сгенерировать командой `docker-compose exec web python -c 'print(__import__("django.core.management.utils", fromlist=[""]).get_random_secret_key())'`

## Документация по API

Документация по API доступна по пути /api/docs/ в развёрнутом проекте.
