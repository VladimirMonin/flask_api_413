from models import (
    Groups,
    Students,
    OnlineLessons,
    StudentsOnlineLessons,
    Homeworks,
    HomeworksStudents,
    StudentsReviews,
)

##################### SELECT ЗАПРОСЫ #####################

# 1. SELECT FROM Groups WHERE group_name = 'python413'
from peewee import DoesNotExist

group_name = "python413"
# Попробуем добыть группу по названию
try:
    group = Groups.get(group_name=group_name)
except DoesNotExist:
    group = None

print(f'Результат поиска группы по запросу "{group_name}": {group}')

print(type(group))

# Получим данные
if group:
    print(f"Группа: {group.group_name}")
    print(f"Дата создания: {group.created_at}")


# 2. SELECT FROM Groups WHERE group_name LIKE '%python%'
group_name_like = "python"

# Получим все группы, где название содержит 'python'
# Тут мы добываем коллекцию объектов, а не один объект
groups_like = Groups.select().where(Groups.group_name.contains(group_name_like))

# Получаем один объект, который соответствует условию. Первый найденный
groups_like2 = Groups.get(Groups.group_name.contains("413"))

print(type(groups_like))
print(type(groups_like2))

print(f"Содержание переменной groups_like: {groups_like}")
print(f"Содержание переменной groups_like2: {groups_like2}")

# Попробуем полуить длинну коллекции и элемент по индексу
print(f"Длинна коллекции groups_like: {len(groups_like)}")
if len(groups_like) > 0:
    print(f"Первый элемент коллекции groups_like: {groups_like[0]}")


# Попробуем у индекса 0 получить атрибут group_name
if len(groups_like) > 0:
    print(
        f"Название группы из первого элемента коллекции groups_like: {groups_like[0]}"
    )

# Возьму первый элемент коллекции groups_like и воспользуюсь его backref="students" (описан в модели Students) - чтобы без JOIN получить студентов группы
group_0 = groups_like[0]
all_students = (
    group_0.students
)  # Получаем всех студентов группы (Экземпляр ModelSelect)")

[print(f"{student.first_name} {student.last_name}") for student in all_students]

# 3. Пробуем "ленивость SELECT накинум WHERE в нескольких строках"
where_1 = "python"
where_2 = "413"

# Получаем все группы через селект.
all_groups = Groups.select()

# Накинем первый WHERE
all_groups = all_groups.where(Groups.group_name.contains(where_1))

# Накинем второй WHERE
all_groups = all_groups.where(Groups.group_name.contains(where_2))

# Получим тип данных, длину, и циклом распечатаем
print(f"Тип данных all_groups: {type(all_groups)}")
print(f"Длинна коллекции all_groups: {len(all_groups)}")

[print(group) for group in all_groups]


# 4. Выборка ВСЕ СТУДЕТЫ + JOIN GROUPS - чтобы отобразить читаемые названия групп
group_name = "python413"
group = Groups.get(Groups.group_name == group_name)

# Выборка всех студентов из группы python413
all_students = (
    Students.select()
)  # Доступ к названим групп тут будет, НО для каждого студента будет отдельный запрос к БД

# Выборка студентов из группы python413 если у нас на руках есть объект группы
students_413 = Students.select().where(Students.group_id == group)


# Если у нас только название группы в виде строки, то нам нужен явный JOIN
# Так же эта штука поможет решить проблему N+1 запросов, когда мы получаем студентов и для каждого студента делаем отдельный запрос к БД для получения названия группы (как в прошлом примере)
students_413 = Students.select().join(Groups).where(Groups.group_name == group_name)

# Тесты - просто подствим сюда разные переменные выше из пункта 4
print(f"Тип данных all_students: {type(students_413)}")
print(f"Длинна коллекции all_students: {len(students_413)}")

[
    print(f"{student.first_name} {student.last_name} - {student.group_id.group_name}")
    for student in students_413
]


# 5. Выборка из студентов полей first_name, last_name из таблицы Groups group_name
students_413 = (
    Students.select(Students.first_name, Students.last_name, Groups.group_name)
    .join(Groups)
    .where(Groups.group_name == group_name)
)

for student in students_413:
    print(f"{student.first_name} {student.last_name} - {student.group_id.group_name}")

# Отличия JOIN и prefetch запросов. Первый делает один бользой запрос. Могут быть некоторые искажения данных при большом количестве связанных объектов.
# Второй делает 2 запроса, извлекая данные о основной таблице, а потом отдельно связанные данные. Это более безопасно, более чистые данные, меньше рисков искажений.

# Как вы видели, можно обойтись ВООБЩЕ БЕЗ ЭТИХ инструментов, но тогда будет N+1 запросов к БД, что неэффективно. Для каждого студента будет отдельный запрос к БД для получения названия группы.

# 6. Выборка студентов с использованием prefetch
students_413 = (
    Students.select()
    .join(Groups)
    .where(Groups.group_name == "python413")
    .prefetch(Groups)
)

for student in students_413:
    print(f"{student.first_name} {student.last_name} - {student.group_id.group_name}")


# SELECT и ЛОГИЧЕСКИЕ ОПЕРАТОРЫ ##############################################################
# **Операторы сравнения:**

# - `Model.field == value`: Равно (`=`). Пример: `User.select().where(User.username == 'Charlie')`.13
# - `Model.field!= value`: Не равно (`!=`). Пример: `User.select().where(User.status!= 'inactive')`.13
# - `Model.field > value`: Больше (`>`). Пример: `Product.select().where(Product.price > 100.0)`.13
# - `Model.field < value`: Меньше (`<`). Пример: `Event.select().where(Event.date < date(2023, 1, 1))`.13
# - `Model.field >= value`: Больше или равно (`>=`)..13
# - `Model.field <= value`: Меньше или равно (`<=`)..13

# **Операторы принадлежности:**

# - `Model.field << [...]` или `Model.field.in_([...])`: Значение поля содержится в списке (SQL `IN`). Пример: `User.select().where(User.status.in_(['active', 'pending']))`.13
# - `Model.field.not_in_([...])`: Значение поля не содержится в списке (SQL `NOT IN`). Пример: `Tweet.select().where(Tweet.user.not_in(banned_users_query))`.13

# **Проверка на `NULL`:**

# - `Model.field >> None` или `Model.field.is_null(True)`: Поле имеет значение `NULL` (SQL `IS NULL`). Пример: `Product.select().where(Product.description.is_null(True))`.13
# - `Model.field.is_null(False)`: Поле не имеет значения `NULL` (SQL `IS NOT NULL`). Пример: `Order.select().where(Order.shipped_date.is_null(False))`.13

# Строковые операции:

# Поведение строковых операций, таких как LIKE, может зависеть от используемой СУБД и ее настроек (например, чувствительность к регистру). В SQLite операция LIKE по умолчанию регистронезависима, в то время как GLOB регистрозависима и использует * и ? в качестве метасимволов вместо % и _.33 Peewee пытается это унифицировать.

# - `Model.field % 'pattern'`: Поиск по шаблону (SQL `LIKE`). `pattern` может содержать метасимволы `%` (любая последовательность символов) и `_` (любой одиночный символ). Пример: `User.select().where(User.email % '%@example.com')`.13
# - `Model.field ** 'pattern'`: Регистронезависимый поиск по шаблону (SQL `ILIKE` в PostgreSQL, или эмулируется через `LOWER()` в других СУБД, если необходимо). Пример: `Book.select().where(Book.title ** '%guide%')`.13
# - `Model.field.contains('substring')`: Поле содержит подстроку (`LIKE '%substring%'`). Пример: `Article.select().where(Article.content.contains('Peewee ORM'))`.13
# - `Model.field.startswith('prefix')`: Поле начинается с префикса (`LIKE 'prefix%'`). Пример: `User.select().where(User.username.startswith('admin_'))`.13
# - `Model.field.endswith('suffix')`: Поле заканчивается суффиксом (`LIKE '%suffix'`). Пример: `File.select().where(File.name.endswith('.txt'))`.13

# **Диапазоны:**

# - `Model.field.between(low, high)`: Значение поля находится в диапазоне между `low` и `high` включительно (SQL `BETWEEN low AND high`). Пример: `Product.select().where(Product.price.between(10.0, 50.0))`.13

# Логические операторы (для объединения выражений):

# Для объединения нескольких условий используются побитовые операторы Python:

# - `&` (логическое И, SQL `AND`): Оба условия должны быть истинны. Пример: `User.select().where((User.is_admin == True) & (User.last_login >= date(2023,1,1)))`.13
# - `|` (логическое ИЛИ, SQL `OR`): Хотя бы одно из условий должно быть истинно. Пример: `User.select().where((User.status == 'admin') | (User.status == 'editor'))`.13
# - `~` (логическое НЕ, SQL `NOT`): Инвертирует условие. Пример: `User.select().where(~(User.email % '%@spam.com'))`.13

# **Важность скобок:** Из-за стандартного приоритета операторов в Python, при комбинировании `&` и `|` в одном выражении необходимо использовать скобки для явного указания порядка выполнения, чтобы избежать неожиданных результатов. Например, `(condition1 & condition2) | condition3` отличается от `condition1 & (condition2 | condition3)`.13

# Одна из частых ошибок, с которой сталкиваются новички, — это попытка использовать стандартные логические операторы Python `and`, `or`, `not` вместо перегруженных Peewee операторов `&`, `|`, `~`. Стандартные операторы Python не могут быть перегружены для построения SQL-выражений и будут интерпретироваться как обычные логические операции Python над результатами выражений (которые обычно приводятся к `True` или `False`), что приведет к неверным SQL-запросам или ошибкам времени выполнения. Поэтому критически важно запомнить и использовать именно `&`, `|` и `~`.

# 7. Найти всех студентов где в first_name входит "алекс" или "влад"
print(f'*' * 50)

students = (
    Students.select()
    .where(
        (Students.first_name.contains("лекс")) | (Students.first_name.contains("лад"))
    )
)

for student in students:
    print(
        f"{student.first_name} {student.last_name} - {student.group_id.group_name}"
    )  # Выводим имя студента и название группы


# 8. Такой же, но с еще поиском по имени группы равенство с "python413"
students = (
    Students.select()
    .join(Groups)
    .where(
        (Students.middle_name.contains("вич")
        & (Groups.group_name == "python413"))
    ).prefetch(Groups) # Используем prefetch для избежания N+1 запросов
)
print(f'*' * 50)
for student in students:
    print(
        f"{student.first_name} {student.middle_name} - {student.group_id.group_name}"
    )  # Выводим имя студента и название группы

###################################### CREATE ЗАПРОСЫ ######################################

# Создание новой группы - самый простой вариант
# new_group = Groups.create(group_name="python412")

# Метод который не создаст объект, если он уже существует
new_group, created = Groups.get_or_create(group_name="python412")

print(f"Группа создана: {created}, объект: {new_group}")

# Переменная под новые группы
new_groups = [
    {"group_name": "python419"},
    {"group_name": "python422"},
]

# Множественное создание групп через bulk_create
new_groups_objects = [Groups(**group) for group in new_groups]

# Создаем группы в БД
# Groups.bulk_create(new_groups_objects)

# Проверим, что группы создались
all_groups = Groups.select()
print(f"Всего групп в БД: {len(all_groups)}")

new_student_data = {
    "first_name": "Фродо",
    "middle_name": "Бильбович",
    "last_name": "Бэггинс",
    "group_name": "python413",
    "notes": "Студент из Шира. Клептоман. Любит драгоценности из золота. Берегите кольца. Обладает невидимостью!",
}

# Создание нового студента
# new_student = Students.create(**new_student_data) # Так можно сделать при совпадении имен полей в модели и словаре

# new_student = Students.create(
#     group_id=Groups.get(Groups.group_name == new_student_data["group_name"]),
#     **new_student_data
# )

# Поиск студента - Бэггинс 
baggins = Students.get(Students.last_name == "Бэггинс")

print(f"Студент найден: {baggins.first_name} {baggins.last_name} {baggins.group_id.group_name}")

# Обновление студента. Изменим заметки по студенту baggins
baggins.notes = "Студент из Шира. После возвращения с Роковой горы стал более сдержанным. Однако серебрянные вилки продолжают пропадать."

# Сохраняем изменения
baggins.save()

# В одну строку добыть, обновить и сохранить
baggins = (
    Students.update(notes="Студент из Шира. После возвращения с Роковой горы стал более сдержанным. Однако серебрянные вилки продолжают пропадать.")
    .where(Students.last_name == "Бэггинс")
    .execute()
)

print(f"Студент обновлен: {baggins} строк(и) изменено")
# После операции обновления, в переменную baggins будет записано количество измененных строк, а не объект студента.

# Удаление студента
baggins = Students.get(Students.last_name == "Бэггинс").delete_instance()

