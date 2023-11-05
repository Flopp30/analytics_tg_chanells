# Userbot. Аналитика ТГ каналов.

### Developers:
- <a href='https://t.me/Flopp'>Floppy</a>
- <a href='https://t.me/maglctea'>FortuAdmin</a>

### Installation

1) Создать файл ```.env``` с переменными окружения в корне проекта. <br>{{значения в этих скобках заменить на свои}}
```
# required
TG_API_ID=
TG_API_HASH=
TG_PHONE_NUMBER=
DJ_DB_URL=postgres://{{db_username}}:{{db_pass}}@127.0.0.1:5432/{{db_name}}
POSTGRES_DB={{db_name}}
POSTGRES_PASSWORD={{db_password}}
POSTGRES_USER={{db_username}}
DJ_ALLOWED_HOSTS=127.0.0.1,{{mydomain.com}}
DJ_CSRF_TRUSTED_ORIGINS={{https://my.domain.com}}

# optional
DJ_DEBUG= # by default: True
DJ_SECRET_KEY=
```

2) Запустить команду в корне проекта 
```
sudo apt install pip docker docker-compose -y && sudo docker-compose up
```
3) Дождаться, пока запустятся контейнеры, после
   - Создаем виртуальное окружение и активируем его
       ```
        python3 -m venv venv && source venv/bin/activate
      ```
   - Устанавливаем зависимости
       ```
        pip install -r requirements.txt
      ```
   - Накатываем миграции
       ```
        python3 manage.py migrate
      ```
   - Создаем суперпользователя
      ```
       python3 manage.py createsuperuser
     ```
   - Запускаем админку
     ```
      python manage.py runserver 127.0.0.1:8000 --noreload
     ```
   - И в другом окне запускаем самого бота
     ```
     python3 manage.py run_bot
     ```

4) В админке после запуска распарсятся все каналы. Рекомендованный алгоритм действий:
- Создайте все необходимые категории. 
В категории есть 2 поля: 
    - chat_id - id chat'а, куда будем пересылать сообщения, превысившие КАП. Можно узнать у <a href='https://t.me/getmyid_bot'>бота</a>
    - name - название категории.
<img src="readme_images/create_category.png"/>
- При обновлении каждого канала укажите созданную подходящую категорию и включите отслеживание.
<img src="readme_images/enable_tracking.png"/>

5) В вынесенных настройках можно поправить процент превышения и интервал запуска второй задачи (5/10 минут)
<img src="readme_images/change_settings.png"/>

### ВАЖНО.
Чтобы настройки вступили в силу в боте: отправьте в saved messages (чат с самим собой) с авторизированного аккаунта команду ```!update_settings```
Чтобы перезапустить задачу с новым интервалом - команда ```!restart_task```<br>
<img src="readme_images/restart_task.png"/>