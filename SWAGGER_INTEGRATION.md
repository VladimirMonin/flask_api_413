# 📚 Интеграция Swagger (OpenAPI) в Flask API с Flask-RESTX: Пошаговое Руководство для Новичков 🚀

Привет! Если ты пишешь API на Flask и хочешь сделать его понятным и удобным для других разработчиков (или для себя в будущем!), то документация — это ключ. Swagger (или OpenAPI) — это мощный инструмент, который автоматически генерирует интерактивную документацию для твоего API. В этом конспекте мы пошагово разберем, как добавить Swagger в твой Flask 3 проект, используя библиотеку `flask-restx`.

## Что такое Swagger/OpenAPI? 🤔

Представь, что у тебя есть инструкция к сложному устройству. Swagger — это такая же инструкция, но для твоего API. Он позволяет:
*   **Видеть все доступные эндпоинты:** Какие адреса есть у твоего API (например, `/group/list/`, `/student/create/`).
*   **Понимать, что они делают:** Какую информацию они ожидают (входные данные) и какую информацию возвращают (выходные данные).
*   **Тестировать API прямо в браузере:** Отправлять запросы и видеть ответы без написания кода.

Это очень удобно!

---

## 🛠️ Итерация 1: Установка Flask-RESTX 📦

Первый шаг — добавить `flask-restx` в твой проект. Это расширение Flask, которое упрощает создание RESTful API и автоматически интегрируется со Swagger.

### 1.1. Установка через pip ⬇️

Открой терминал в корневой папке твоего проекта и выполни следующую команду:

```powershell
pip install flask-restx
```

Эта команда загрузит и установит все необходимые файлы `flask-restx` и его зависимости.

### 1.2. Обновление `requirements.txt` (Опционально, но Рекомендуется) 📝

Чтобы другие разработчики могли легко установить все зависимости твоего проекта, обнови файл `requirements.txt`:

```powershell
pip freeze > requirements.txt
```

Теперь `flask-restx` будет в списке зависимостей.

---

## ⚙️ Итерация 2: Инициализация API в `app.py` 🌐

Теперь, когда `flask-restx` установлен, нам нужно "научить" наше Flask-приложение использовать его для создания API и отображения Swagger UI.

### 2.1. Импорт и Инициализация `Api` ➕

Открой файл `app.py`. Тебе нужно импортировать `Api` из `flask_restx` и инициализировать его, передав ему экземпляр твоего Flask-приложения.

**Было (примерно):**
```python
from flask import Flask, jsonify, request
# ... другие импорты
from groups_bp import groups_bp
from students_bp import students_bp

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
app.register_blueprint(groups_bp)
app.register_blueprint(students_bp)
# ...
```

**Стало:**
```python
from flask import Flask, jsonify, request
from flask_restx import Api # 👈 Добавляем этот импорт
from utils import get_group_by_id, get_groups_list, get_student_by_id, create_group, update_group_id, delete_group_id, create_student
from peewee import DoesNotExist, IntegrityError
from groups_bp import groups_bp # 👈 Эти импорты Blueprint пока оставляем
from students_bp import students_bp # 👈 Эти импорты Blueprint пока оставляем

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

# 🚀 Инициализируем Api для Swagger
api = Api(
    app,
    version='1.0',
    title='Academy API',
    description='Документация для API управления академией',
    doc='/swaggerui/' # 👈 Здесь будет доступен Swagger UI
)

# Регистрация Blueprint (пока оставляем, но скоро изменим)
app.register_blueprint(groups_bp)
app.register_blueprint(students_bp)

if __name__ == "__main__":
    app.run(debug=True)
```

**Что мы сделали?**
*   Импортировали `Api`.
*   Создали экземпляр `Api`, передав ему `app`.
*   Указали `version`, `title` и `description` — это информация, которая будет отображаться в заголовке твоей Swagger-документации.
*   Самое главное: `doc='/swaggerui/'` — это путь, по которому будет доступен интерактивный интерфейс Swagger UI. После запуска приложения ты сможешь открыть его в браузере по адресу `http://127.0.0.1:5000/swaggerui/` (если твой Flask работает на порту 5000).

---

## 🔄 Итерация 3: Преобразование Blueprints в Namespaces 🏷️

`flask-restx` использует концепцию "Namespaces" (пространств имен) вместо стандартных Flask Blueprints для организации API. Это позволяет лучше структурировать документацию.

### 3.1. Изменение `groups_bp.py` 🧑‍🤝‍🧑

Открой файл `groups_bp.py`. Нам нужно изменить его так, чтобы он использовал `Namespace` из `flask_restx`.

**Было (начало файла):**
```python
from utils import get_group_by_id, get_groups_list, create_group, update_group_id, delete_group_id
from flask import Blueprint, jsonify, request
from peewee import DoesNotExist, IntegrityError
from utils import check_access

groups_bp = Blueprint('groups', __name__, url_prefix='/group')
```

**Стало (начало файла):**
```python
from flask_restx import Namespace, Resource, fields # 👈 Новые импорты
from flask import request # 👈 Убираем jsonify
from peewee import DoesNotExist, IntegrityError
from utils import get_group_by_id, get_groups_list, create_group, update_group_id, delete_group_id
from utils import check_access # 👈 Пока оставляем, но скоро удалим

# 🚀 Импортируем объект api из app.py
from app import api

# 🏷️ Создаем Namespace вместо Blueprint
ns_groups = api.namespace('groups', description='Операции с группами') # 👈 Меняем groups_bp на ns_groups
```

**Что мы сделали?**
*   Импортировали `Namespace`, `Resource`, `fields`.
*   **Важно:** Импортировали `api` из `app`. Это тот самый объект `Api`, который мы инициализировали в `app.py`.
*   Создали `ns_groups = api.namespace(...)` — это наш новый "Blueprint" для групп.
*   Убрали `jsonify` из импортов Flask, так как `flask-restx` сам занимается сериализацией ответов.

### 3.2. Изменение `students_bp.py` 🎓

Аналогично, открой файл `students_bp.py` и внеси похожие изменения.

**Было (начало файла):**
```python
from utils import  get_student_by_id, create_student
from flask import Blueprint, jsonify, request
from peewee import DoesNotExist, IntegrityError

students_bp = Blueprint('students', __name__, url_prefix='/student')
```

**Стало (начало файла):**
```python
from flask_restx import Namespace, Resource, fields # 👈 Новые импорты
from flask import request # 👈 Убираем jsonify
from peewee import DoesNotExist, IntegrityError
from utils import get_student_by_id, create_student

# 🚀 Импортируем объект api из app.py
from app import api

# 🏷️ Создаем Namespace вместо Blueprint
ns_students = api.namespace('students', description='Операции со студентами') # 👈 Меняем students_bp на ns_students
```

### 3.3. Обновление `app.py` для использования Namespaces 🔄

Теперь, когда у нас есть Namespaces, нам нужно "зарегистрировать" их в объекте `api` в `app.py` вместо старых Blueprints.

**Было (в `app.py`):**
```python
# Регистрация Blueprint
app.register_blueprint(groups_bp)
app.register_blueprint(students_bp)
```

**Стало (в `app.py`):**
```python
# 🚀 Импортируем Namespaces
from groups_bp import ns_groups
from students_bp import ns_students

# 🔗 Добавляем Namespaces к объекту api
api.add_namespace(ns_groups)
api.add_namespace(ns_students)
```

**Что мы сделали?**
*   Импортировали `ns_groups` и `ns_students` (наши новые Namespaces).
*   Использовали `api.add_namespace()` для их регистрации. Теперь `flask-restx` знает о наших API-маршрутах.

---

## 📝 Итерация 4: Документирование Моделей Данных 📊

Для того чтобы Swagger мог правильно отображать, какие данные ожидаются на вход и какие возвращаются на выход, нам нужно описать структуры этих данных. `flask-restx` делает это с помощью `api.model` и `fields`.

### 4.1. Модель `Group` в `groups_bp.py` 🧑‍🤝‍🧑

В файле `groups_bp.py`, после инициализации `ns_groups`, но до определения маршрутов, добавь описание модели `Group`.

```python
# ... (импорты и ns_groups)

# 📊 Модель для ответа (выходные данные)
group_model = ns_groups.model('Group', {
    'id': fields.Integer(readOnly=True, description='Уникальный идентификатор группы'),
    'group_name': fields.String(required=True, description='Название группы'),
    'created_at': fields.String(description='Дата и время создания группы (ISO 8601)'),
})

# 📥 Модель для запроса (входные данные)
group_input_model = ns_groups.model('GroupInput', {
    'group_name': fields.String(required=True, description='Название группы'),
})
```

**Что мы сделали?**
*   `group_model`: Описывает, как будет выглядеть объект группы в ответе API. `readOnly=True` означает, что это поле только для чтения (клиент не должен его отправлять).
*   `group_input_model`: Описывает, какие поля ожидаются в теле запроса при создании или обновлении группы. `required=True` указывает, что поле обязательно.

### 4.2. Модель `Student` в `students_bp.py` 🎓

Аналогично, в файле `students_bp.py`, после инициализации `ns_students`, добавь описание модели `Student`.

```python
# ... (импорты и ns_students)

# 📊 Модель для ответа (выходные данные)
student_model = ns_students.model('Student', {
    'id': fields.Integer(readOnly=True, description='Уникальный идентификатор студента'),
    'first_name': fields.String(required=True, description='Имя студента'),
    'middle_name': fields.String(description='Отчество студента (опционально)'),
    'last_name': fields.String(required=True, description='Фамилия студента'),
    'group_id': fields.Integer(required=True, description='ID группы, к которой принадлежит студент'),
    'group_name': fields.String(description='Название группы'),
    'notes': fields.String(description='Дополнительные заметки о студенте'),
    'created_at': fields.String(description='Дата и время создания студента (ISO 8601)'),
})

# 📥 Модель для запроса (входные данные)
student_input_model = ns_students.model('StudentInput', {
    'first_name': fields.String(required=True, description='Имя студента'),
    'middle_name': fields.String(description='Отчество студента (опционально)'),
    'last_name': fields.String(required=True, description='Фамилия студента'),
    'group_id': fields.Integer(required=True, description='ID группы, к которой принадлежит студент'),
    'notes': fields.String(description='Дополнительные заметки о студенте'),
})
```

---

## 🎯 Итерация 5: Документирование Эндпоинтов и Параметров 📄

Теперь мы перейдем к самому интересному — документированию каждого API-эндпоинта. Мы будем использовать декораторы `flask-restx` для описания маршрутов, ожидаемых параметров и возвращаемых значений.

### 5.1. Изменение `groups_bp.py` 🧑‍🤝‍🧑

Каждый маршрут Flask (`@groups_bp.route(...)`) будет преобразован в класс `Resource` с методами для каждого HTTP-глагола (GET, POST, PUT, DELETE).

**Пример преобразования GET-маршрута:**

**Было:**
```python
@groups_bp.route("/<int:group_id>", methods=["GET"])
def get_group(group_id):
    # ...
    return jsonify(group_dict), 200
```

**Стало:**
```python
from http import HTTPStatus # 👈 Добавляем импорт для статусов HTTP

@ns_groups.route("/<int:group_id>") # 👈 Используем ns_groups.route
@ns_groups.param('group_id', 'Уникальный идентификатор группы') # 👈 Документируем параметр пути
class GroupItem(Resource): # 👈 Создаем класс Resource
    @ns_groups.doc('Получить информацию о группе по ID') # 👈 Описание эндпоинта
    @ns_groups.marshal_with(group_model, code=HTTPStatus.OK) # 👈 Описываем формат ответа (200 OK)
    def get(self, group_id): # 👈 Метод GET
        try:
            group = get_group_by_id(group_id)
        except DoesNotExist:
            ns_groups.abort(HTTPStatus.NOT_FOUND, "Группа не найдена") # 👈 Используем abort для ошибок
        return group # 👈 Возвращаем объект Peewee, flask-restx его сериализует
```

**Основные изменения:**
*   `@ns_groups.route(...)`: Используем маршрутизатор Namespace.
*   `@ns_groups.param(...)`: Документируем параметры пути (например, `group_id`).
*   `class GroupItem(Resource):`: Создаем класс, наследующийся от `Resource`.
*   `@ns_groups.doc(...)`: Добавляем общее описание для операции.
*   `@ns_groups.marshal_with(group_model, code=HTTPStatus.OK)`: Указываем, что этот эндпоинт возвращает данные в формате `group_model` при успешном выполнении (статус 200 OK).
*   `def get(self, group_id):`: Метод `get` обрабатывает GET-запросы.
*   `ns_groups.abort(...)`: Используем для возврата ошибок с соответствующим HTTP-статусом и сообщением. Это автоматически генерирует правильный ответ JSON.
*   Возвращаем сам объект `group` из Peewee, а `marshal_with` позаботится о его преобразовании в JSON согласно `group_model`.

**Полный код `groups_bp.py` после изменений:**

```python
from flask_restx import Namespace, Resource, fields
from flask import request
from peewee import DoesNotExist, IntegrityError
from utils import get_group_by_id, get_groups_list, create_group, update_group_id, delete_group_id
from utils import check_access # Пока оставляем, но скоро удалим
from app import api
from http import HTTPStatus # Добавляем импорт для статусов HTTP

ns_groups = api.namespace('groups', description='Операции с группами')

# 📊 Модель для ответа (выходные данные)
group_model = ns_groups.model('Group', {
    'id': fields.Integer(readOnly=True, description='Уникальный идентификатор группы'),
    'group_name': fields.String(required=True, description='Название группы'),
    'created_at': fields.String(description='Дата и время создания группы (ISO 8601)'),
})

# 📥 Модель для запроса (входные данные)
group_input_model = ns_groups.model('GroupInput', {
    'group_name': fields.String(required=True, description='Название группы'),
})

# 🔑 Модель для ошибки доступа
access_denied_model = ns_groups.model('AccessDenied', {
    'error': fields.String(description='Сообщение об ошибке доступа')
})

@ns_groups.route("/<int:group_id>")
@ns_groups.param('group_id', 'Уникальный идентификатор группы')
class GroupItem(Resource):
    @ns_groups.doc('Получить информацию о группе по ID')
    @ns_groups.marshal_with(group_model, code=HTTPStatus.OK)
    @ns_groups.response(HTTPStatus.NOT_FOUND, 'Группа не найдена')
    @ns_groups.response(HTTPStatus.FORBIDDEN, 'Доступ запрещен', model=access_denied_model) # Добавляем документацию для 403
    def get(self, group_id):
        # Проверяем доступ пользователя
        if not check_access(request, "user"):
            ns_groups.abort(HTTPStatus.FORBIDDEN, "Доступ запрещен")

        try:
            group = get_group_by_id(group_id)
        except DoesNotExist:
            ns_groups.abort(HTTPStatus.NOT_FOUND, "Группа не найдена")
        return group

@ns_groups.route("/list/")
class GroupList(Resource):
    @ns_groups.doc('Получить список всех групп')
    @ns_groups.param('sort_direction', 'Направление сортировки (asc/desc)', type=str, default='asc')
    @ns_groups.param('name_filter', 'Фильтр по названию группы', type=str)
    @ns_groups.marshal_list_with(group_model, code=HTTPStatus.OK) # marshal_list_with для списка объектов
    def get(self):
        sort_direction = request.args.get("sort_direction", "asc")
        name_filter = request.args.get("name_filter")

        if sort_direction not in ["asc", "desc"]:
            ns_groups.abort(HTTPStatus.BAD_REQUEST, "Неверное направление сортировки")

        groups = get_groups_list(sort_direction, name_filter)
        return groups # Возвращаем список объектов Peewee

@ns_groups.route("/create/")
class GroupCreate(Resource):
    @ns_groups.doc('Создать новую группу')
    @ns_groups.expect(group_input_model, validate=True) # Ожидаем данные в формате group_input_model
    @ns_groups.marshal_with(group_model, code=HTTPStatus.CREATED) # 201 Created
    @ns_groups.response(HTTPStatus.BAD_REQUEST, 'Название группы обязательно или группа с таким названием уже существует')
    def post(self):
        data = request.get_json()
        group_name = data.get("group_name")

        if not group_name:
            ns_groups.abort(HTTPStatus.BAD_REQUEST, "Название группы обязательно")

        try:
            group = create_group(group_name)
        except IntegrityError:
            ns_groups.abort(HTTPStatus.BAD_REQUEST, "Группа с таким названием уже существует")
        return group

@ns_groups.route("/update/<int:group_id>")
@ns_groups.param('group_id', 'Уникальный идентификатор группы')
class GroupUpdate(Resource):
    @ns_groups.doc('Обновить информацию о группе по ID')
    @ns_groups.expect(group_input_model, validate=True)
    @ns_groups.marshal_with(group_model, code=HTTPStatus.OK)
    @ns_groups.response(HTTPStatus.NOT_FOUND, 'Группа не найдена')
    @ns_groups.response(HTTPStatus.BAD_REQUEST, 'Название группы обязательно или группа с таким названием уже существует')
    def put(self, group_id):
        data = request.get_json()
        group_name = data.get("group_name")

        if not group_name:
            ns_groups.abort(HTTPStatus.BAD_REQUEST, "Название группы обязательно")

        try:
            updated_group = update_group_id(group_id, group_name)
        except DoesNotExist:
            ns_groups.abort(HTTPStatus.NOT_FOUND, "Группа не найдена")
        except IntegrityError:
            ns_groups.abort(HTTPStatus.BAD_REQUEST, "Группа с таким названием уже существует")
        return updated_group

@ns_groups.route("/delete/<int:group_id>")
@ns_groups.param('group_id', 'Уникальный идентификатор группы')
class GroupDelete(Resource):
    @ns_groups.doc('Удалить группу по ID')
    @ns_groups.response(HTTPStatus.OK, 'Группа успешно удалена')
    @ns_groups.response(HTTPStatus.NOT_FOUND, 'Группа не найдена')
    def delete(self, group_id):
        try:
            delete_group_id(group_id)
        except DoesNotExist:
            ns_groups.abort(HTTPStatus.NOT_FOUND, "Группа не найдена")
        return {"message": "Группа успешно удалена"}, HTTPStatus.OK
```

### 5.2. Изменение `students_bp.py` 🎓

Аналогично, преобразуем маршруты студентов в классы `Resource`.

**Полный код `students_bp.py` после изменений:**

```python
from flask_restx import Namespace, Resource, fields
from flask import request
from peewee import DoesNotExist, IntegrityError
from utils import get_student_by_id, create_student
from app import api
from http import HTTPStatus

ns_students = api.namespace('students', description='Операции со студентами')

# 📊 Модель для ответа (выходные данные)
student_model = ns_students.model('Student', {
    'id': fields.Integer(readOnly=True, description='Уникальный идентификатор студента'),
    'first_name': fields.String(required=True, description='Имя студента'),
    'middle_name': fields.String(description='Отчество студента (опционально)'),
    'last_name': fields.String(required=True, description='Фамилия студента'),
    'group_id': fields.Integer(required=True, description='ID группы, к которой принадлежит студент'),
    'group_name': fields.String(description='Название группы'),
    'notes': fields.String(description='Дополнительные заметки о студенте'),
    'created_at': fields.String(description='Дата и время создания студента (ISO 8601)'),
})

# 📥 Модель для запроса (входные данные)
student_input_model = ns_students.model('StudentInput', {
    'first_name': fields.String(required=True, description='Имя студента'),
    'middle_name': fields.String(description='Отчество студента (опционально)'),
    'last_name': fields.String(required=True, description='Фамилия студента'),
    'group_id': fields.Integer(required=True, description='ID группы, к которой принадлежит студент'),
    'notes': fields.String(description='Дополнительные заметки о студенте'),
})

@ns_students.route("/<int:student_id>")
@ns_students.param('student_id', 'Уникальный идентификатор студента')
class StudentItem(Resource):
    @ns_students.doc('Получить информацию о студенте по ID')
    @ns_students.marshal_with(student_model, code=HTTPStatus.OK)
    @ns_students.response(HTTPStatus.NOT_FOUND, 'Студент не найден')
    def get(self, student_id):
        student = get_student_by_id(student_id)
        if not student:
            ns_students.abort(HTTPStatus.NOT_FOUND, "Студент не найден")
        return student

@ns_students.route("/create/")
class StudentCreate(Resource):
    @ns_students.doc('Создать нового студента')
    @ns_students.expect(student_input_model, validate=True)
    @ns_students.marshal_with(student_model, code=HTTPStatus.CREATED)
    @ns_students.response(HTTPStatus.BAD_REQUEST, 'Имя, фамилия и ID группы обязательны или группа не найдена')
    def post(self):
        data = request.get_json()
        first_name = data.get("first_name")
        middle_name = data.get("middle_name")
        last_name = data.get("last_name")
        group_id = data.get("group_id")
        notes = data.get("notes")

        if not first_name or not last_name or not group_id:
            ns_students.abort(HTTPStatus.BAD_REQUEST, "Имя, фамилия и ID группы обязательны")

        try:
            student = create_student(first_name, last_name, group_id, middle_name, notes)
        except DoesNotExist:
            ns_students.abort(HTTPStatus.BAD_REQUEST, "Группа не найдена")
        except Exception as e:
            ns_students.abort(HTTPStatus.BAD_REQUEST, str(e))
        return student
```

---

## 🔑 Итерация 6: Добавление Авторизации API Key 🛡️

Если твой API использует ключи доступа (API Keys), ты можешь добавить их описание в Swagger UI, чтобы пользователи могли тестировать защищенные эндпоинты.

### 6.1. Обновление `app.py` для API Key 🔐

В файле `app.py`, при инициализации `Api`, добавь параметры `security` и `authorizations`.

**Было (в `app.py`):**
```python
api = Api(
    app,
    version='1.0',
    title='Academy API',
    description='Документация для API управления академией',
    doc='/swaggerui/'
)
```

**Стало (в `app.py`):**
```python
from flask import Flask, jsonify, request
from flask_restx import Api, fields # 👈 Добавляем fields для модели ошибки
from utils import get_group_by_id, get_groups_list, get_student_by_id, create_group, update_group_id, delete_group_id, create_student
from peewee import DoesNotExist, IntegrityError
from groups_bp import ns_groups # 👈 Импортируем Namespaces
from students_bp import ns_students # 👈 Импортируем Namespaces

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

# 🔑 Определяем схему авторизации API Key
authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API-KEY', # Имя заголовка, в котором передается ключ
        'description': 'API Key для доступа к защищенным эндпоинтам'
    }
}

api = Api(
    app,
    version='1.0',
    title='Academy API',
    description='Документация для API управления академией',
    doc='/swaggerui/',
    security='apikey', # 👈 Указываем, что по умолчанию используется схема 'apikey'
    authorizations=authorizations # 👈 Передаем описание схем авторизации
)

# 🔗 Добавляем Namespaces к объекту api
api.add_namespace(ns_groups)
api.add_namespace(ns_students)

if __name__ == "__main__":
    app.run(debug=True)
```

**Что мы сделали?**
*   Определили словарь `authorizations`, который описывает, как работает наш API Key (тип `apiKey`, передается в заголовке `X-API-KEY`).
*   Передали этот словарь в `Api` и указали `security='apikey'`, чтобы все эндпоинты по умолчанию требовали этот ключ.

### 6.2. Документирование защищенных эндпоинтов (опционально) 🔒

Если у тебя есть эндпоинты, которые требуют авторизации, ты можешь явно указать это с помощью декоратора `@api.doc(security='apikey')` или `@api.doc(security=[{'apikey': []}])`. В нашем случае, поскольку мы указали `security='apikey'` при инициализации `Api`, все эндпоинты уже будут помечены как защищенные.

---

## 🧹 Итерация 7: Удаление Устаревшего Кода (check_access) 🗑️

В процессе рефакторинга мы заметили, что функция `check_access` в `utils.py` больше не используется напрямую в `groups_bp.py` (поскольку мы перешли на `flask-restx.abort` для обработки ошибок доступа). Чтобы код был чистым, ее можно удалить.

### 7.1. Удаление `check_access` из `utils.py` ❌

Открой файл `utils.py` и удали функцию `check_access` и ее импорт `Literal`.

**Было (в `utils.py`):**
```python
# ...
from api_keys import users
from typing import Literal # 👈 Удаляем этот импорт

# Функция которая принемает request и роль и возвращает True если у пользователя есть доступ, иначе False
def check_access(request, role: Literal["admin", "moderator", "user"]) -> bool:
    # ... код функции
```

**Стало (в `utils.py`):**
```python
# ...
from api_keys import users
# 👈 Удаляем функцию check_access полностью
```

**Что мы сделали?**
*   Удалили неиспользуемую функцию `check_access` и связанный импорт `Literal`, чтобы код был более чистым и поддерживаемым.

---

## 🐛 Итерация 8: Исправление Ошибок Линтера (id = AutoField()) 🛠️

При работе с `peewee` и некоторыми линтерами (например, Pylance) может возникать предупреждение о том, что у моделей нет атрибута `id`, хотя `peewee` автоматически добавляет его как первичный ключ. Чтобы убрать это предупреждение и сделать код более явным, мы можем явно определить `id` в моделях.

### 8.1. Добавление `id = AutoField()` в `models.py` 🆔

Открой файл `models.py` и добавь `id = AutoField()` в каждую модель, где `id` является первичным ключом (обычно это все модели).

**Было (в `models.py` для `Groups`):**
```python
class Groups(Model):
    group_name = CharField(unique=True, null=False, max_length=50)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    # ...
```

**Стало (в `models.py` для `Groups`):**
```python
from peewee import * # 👈 Убедись, что AutoField импортирован
import datetime

# ...

# Группы
class Groups(Model):
    id = AutoField() # 👈 Добавляем эту строку
    group_name = CharField(unique=True, null=False, max_length=50)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    # ...
```

Повтори это для всех моделей (`Students`, `OnlineLessons`, `StudentsOnlineLessons`, `Homeworks`, `HomeworksStudents`, `StudentsReviews`).

**Что мы сделали?**
*   Явно указали, что `id` является полем `AutoField`, что помогает линтерам правильно понимать структуру модели и убирает ложные предупреждения.

---

## 🏁 Запуск и Проверка! 🎉

Теперь, когда все изменения внесены, ты можешь запустить свое Flask-приложение:

```powershell
python app.py
```

Открой браузер и перейди по адресу `http://127.0.0.1:5000/swaggerui/`. Ты должен увидеть интерактивную документацию своего API!

### Пример того, что ты увидишь в Swagger UI:

```mermaid
graph TD
    A[Academy API] --> B(Groups Namespace);
    A --> C(Students Namespace);

    B --> B1(GET /group/{group_id});
    B --> B2(GET /group/list/);
    B --> B3(POST /group/create/);
    B --> B4(PUT /group/update/{group_id});
    B --> B5(DELETE /group/delete/{group_id});

    C --> C1(GET /student/{student_id});
    C --> C2(POST /student/create/);

    B1 -- "Параметры: group_id" --> B1_Doc(Документация: Получить информацию о группе);
    B3 -- "Тело запроса: GroupInput" --> B3_Doc(Документация: Создать новую группу);
    B3_Doc -- "Ответ: Group" --> B3_Resp(Статус: 201 Created);
```

### Таблица изменений файлов:

