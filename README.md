# Проект CookBooker 

## Описание:
Проект "CookBooker" – это сервис, который даёт возможность людям делиться рецептами, и создавать свои списки покупок, для упрощения похода в магазин.

## Стек проекта:
- Python 
- Docker 
- Django 
- Nginx 
- Gunicorn
- REST framework
- Djoser

## Документация API

### При локальном запуске проекта статическая документация доступна 
### по адресу:
http://127.0.0.1:7000/api/docs/redoc.html

## Запуск проекта локально

### Клонировать репозиторий:
https://github.com/SabinaDzh/foodgram.git

### Перейти в корневую директорию проекта:
cd foodgram/

## Установка докера:
```sh
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt install docker-compose-plugin 
```

### Создайте собственный файл .env с переменными окружения.

### Соберите образы и отправьте их в Docker Hub, заменив username 
### на свой:
```sh
cd frontend
docker build -t username/foodgram_frontend .
docker push username/foodgram_frontend
cd ../backend
docker build -t username/foodgram_backend .
docker push username/foodgram_backend
cd ../infra
docker build -t username/foodgram_infra .
docker push username/foodgram_infra
```
### В файле docker-compose.yml укажите нужные образы.

## Процесс запуска проекта: 

```sh
sudo docker compose -f docker-compose.yml up
sudo docker compose -f docker-compose.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```
## Создаем суперпользователя
```sh
sudo docker compose exec backend python manage.py createsuperuser
```
## Наполняем БД даннымии из файла data/ingredients.csv
```sh
sudo docker compose exec python manage.py load_ingredients_tags
```
## Примеры запросов:

### Создание рецепта
    POST /api/recipes/
    Content-Type: application/json
    {
    "ingredients": [
        {
        "id": 1,
        "amount": 11
        },
    ],
    "tags": [
        1
    ],
        "image": "data:image/png,
    "name": "Нечто съедобное (это не точно)",
    "text": "Приготовьте как нибудь эти ингредиеты",
    "cooking_time": 5
    }

### Получение всех рецептов
    GET /api/recipes/

### Полуение рецепта 
    GET /api/v1/posts/{id}/

### Получение короткой ссылки на рецепт
    GET /api/recipes/{id}/get-link/

### Добавить рецепт в список покупок
    POST /api/recipes/{id}/shopping_cart/
    Content-Type: application/json
    {
    }

### Подписка
    POST /api/users/{id}/subscribe/
    Content-Type: application/json
    {
    }

### Регистрация пользователя
    POST /api/users/
    Content-Type: application/json
    {
    "email": "mitya@ya.ru",
    "username": "mitya.mitya",
    "first_name": "Митя",
    "last_name": "Митин",
    "password": "123qwe!"
    }

### Получения профиля пользователя
    GET /api/users/{id}/

## Ссылка на развернутый проект
(https://foodgram.myddns.me)

## Автор проекта 
SabinaDzh
