
[foodgram](https://github.com/agamova/foodgram-project-react/workflows/main.yaml/badge.svg)

# Foodgram - продуктовый помощник.

«Продуктовый помощник» - сайт, на котором пользователи будут публиковать рецепты,
добавлять чужие рецепты в избранное и подписываться на публикации других авторов.
Сервис «Список покупок» позволит пользователям создавать список продуктов, 
которые нужно купить для приготовления выбранных блюд.

### Для запуска проекта на удаленном сервере:

Склонируйте репозиторий  на локальный компьютер

```
git clone https://github.com/agamova/foodgram-project-react
```

В файле infra/nginx.conf укажите IP-адрес вашего сервера. Скопируйте файлы 
infra/nginx.conf и infra/docker-compose.yml в корневую директорию сервера. Там 
же создайте файл .env по шаблону .env.template.
На сервере должны быть установлены docker и docker-compose.

Для запуска контейнеров выполните
```
sudo docker-compose up -d --build
```
После успешного запуска на сервере выполните команды (только после первого деплоя):

```
sudo docker-compose exec web python manage.py collectstatic
```
```
sudo docker-compose exec web python manage.py migrate
```
```
sudo docker-compose exec web python manage.py loader_csv
```
```
sudo docker-compose exec web python manage.py createsuperuser
```