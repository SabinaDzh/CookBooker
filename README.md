# Проект Foodgram

## Описание
Проект "Foodgram" – это сервис, который даёт возможность людям делиться рецептами, и создавать свои списки покупок, для упрощения похода в магазин.

## Стек проекта
- Python 
- Docker 
- Django 
- Nginx 
- Gunicorn
- REST framework
- Djoser

## Ссылка на развернутый проект
(https://foodgram.myddns.me)

## Клонировать репозиторий
https://github.com/SabinaDzh/foodgram.git

## Процесс запуска проекта 

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

## Автор проекта 
 
SabinaDzh
