"""
Модуль utils.py

Содержит функции для работы с моделями базы данных (Groups, Students) с использованием ORM peewee.

Функции:

get_group_by_id(group_id: int) -> Optional[Groups]
    Возвращает группу по ID или None, если не найдено.

create_group(group_name: str) -> Groups
    Создаёт новую группу с заданным именем.

delete_group_id(group_id: int) -> bool
    Удаляет группу по ID. Возвращает True при успехе.

update_group_id(group_id: int, new_group_name: str) -> Optional[Groups]
    Обновляет имя группы по ID. Возвращает обновлённую группу.

get_groups_list(sort_direction: str = "asc", name_filter: Optional[str] = None) -> list
    Возвращает список групп с возможностью сортировки и фильтрации по имени.

get_student_by_id(student_id: int, expand_fields: Optional[List[str]] = None) -> Optional[Dict[str, Any]]
    Возвращает студента по ID с возможностью раскрытия связанных объектов.

create_student(first_name: str, last_name: str, group_id: int, middle_name: Optional[str] = None, notes: Optional[str] = None) -> Dict[str, Any]
    Создаёт нового студента.

update_student_by_id(student_id: int, **kwargs) -> Optional[Dict[str, Any]]
    Обновляет данные студента по ID.

delete_student_by_id(student_id: int) -> bool
    Удаляет студента по ID. Возвращает True при успехе.

get_students_list(group_id: Optional[int] = None, name_filter: Optional[str] = None, sort_by: str = "last_name", sort_direction: str = "asc", expand_fields: Optional[List[str]] = None, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Students]
    Возвращает список студентов с фильтрацией, сортировкой и пагинацией.

get_students_by_group_name(group_name: str, expand_fields: Optional[List[str]] = None) -> List[Dict[str, Any]]
    Возвращает список студентов по названию группы.
"""

from models import Groups, Students
from peewee import DoesNotExist, IntegrityError
import json
import datetime
from typing import Optional, List, Dict, Any
from api_keys import users
from typing import Literal


# Функция которая принемает request и роль и возвращает True если у пользователя есть доступ, иначе False
def check_access(request, role: Literal["admin", "moderator", "user"]) -> bool:
    """
    Проверяет доступ пользователя на основе его роли и API ключа.

    Args:
        request: Объект запроса, содержащий заголовки.
        role: Роль пользователя, может быть "admin", "moderator" или "user".

    Returns:
        bool: True, если пользователь имеет доступ, иначе False.
    """
    api_key = request.headers.get("X-API-KEY")
    
    # 1. Найти пользователя
    try: 
        user = next(user for user in users if user["api_key"] == api_key)

    except StopIteration: 
        return False  # Пользователь не найден
    
    # 2. Проверить роль пользователя
    user_role = user["role"]  # Получаем роль пользователя

    # 3. Если пользователь admin, то он имеет доступ к любым данным
    if user_role == "admin":  # Если роль admin, то доступ разрешен
        return True  # Доступ разрешен
    
    # 4. Если пользователь moderator, то он имеет доступ к данным moderator и user
    if user_role == "moderator" and role in ["moderator", "user"]:  # Если роль moderator, то доступ разрешен для
        return True  # Доступ разрешен
    # 5. Если пользователь user, то он имеет доступ только к своим данным
    if user_role == "user" and role == "user":  # Если роль user, то доступ разрешен только для user
        return True  # Доступ разрешен
    
    else:
        return False  # Доступ запрещенq



def get_group_by_id(group_id: int) -> Optional[Groups]:
    """
    Получает группу по ID.
    """
    try:
        group = Groups.get(Groups.id == group_id)
        return group
    except DoesNotExist:
        print(f"Группа с ID {group_id} не найдена.")
        raise


def create_group(group_name: str) -> Groups:
    """
    Создает новую группу с заданным именем.
    """
    try:
        group = Groups.create(group_name=group_name)
        return group
    # IntegrityError - нарушение целостности данных (уникальность, внежний ключ и т.д.)
    except IntegrityError:
        print("Группа с таким именем уже существует.")
        raise


def delete_group_id(group_id: int) -> bool:
    """
    Удаляет группу по ID.
    """
    try:
        group = Groups.get(Groups.id == group_id)
        group.delete_instance()
        return True
    except DoesNotExist:
        print("Группа не найдена.")
        raise
    except IntegrityError:
        print("Невозможно удалить группу, так как она связана с другими записями.")
        raise


def update_group_id(group_id: int, new_group_name: str) -> Optional[Groups]:
    """
    Обновляет имя группы по ID.
    """
    try:
        # Сначала проверим, что группа существует
        group = Groups.get(Groups.id == group_id)

        # Выполняем атомарное обновление
        rows_updated = (
            Groups.update(group_name=new_group_name)
            .where(Groups.id == group_id)
            .execute()
        )

        if rows_updated == 0:
            raise DoesNotExist("Группа не найдена")

        # Получаем обновленную группу
        updated_group = Groups.get(Groups.id == group_id)
        return updated_group

    except DoesNotExist:
        print("Группа не найдена.")
        raise
    except IntegrityError:
        print("Невозможно обновить группу, так как новое имя уже существует.")
        raise


def get_groups_list(
    sort_direction: str = "asc", name_filter: Optional[str] = None
) -> list:
    """
    Получает список групп с возможностью сортировки и фильтрации по имени.
    """
    query = Groups.select()

    if name_filter:
        query = query.where(Groups.group_name.contains(name_filter))

    if sort_direction == "asc":
        query = query.order_by(Groups.group_name.asc())
    elif sort_direction == "desc":
        query = query.order_by(Groups.group_name.desc())

    return list(query)


# ========== ФУНКЦИИ ДЛЯ РАБОТЫ СО СТУДЕНТАМИ ==========


def get_student_by_id(
    student_id: int, expand_fields: Optional[List[str]] = None
) -> Optional[Dict[str, Any]]:
    """
    Получает студента по ID с возможностью раскрытия связанных объектов.

    Args:
        student_id: ID студента
        expand_fields: Список полей для раскрытия (например, ['group'])

    Returns:
        Словарь с данными студента или None если не найден
    """
    try:
        # Используем join для эффективного получения связанных данных
        query = Students.select()
        if expand_fields and "group" in expand_fields:
            query = query.join(Groups)

        student = query.where(Students.id == student_id).get()
        return student
    except DoesNotExist:
        return None


def create_student(
    first_name: str,
    last_name: str,
    group_id: int,
    middle_name: Optional[str] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Создает нового студента.

    Args:
        first_name: Имя
        last_name: Фамилия
        group_id: ID группы
        middle_name: Отчество (опционально)
        notes: Заметки (опционально)

    Returns:
        Словарь с данными созданного студента

    Raises:
        DoesNotExist: Если группа с указанным ID не существует
        IntegrityError: При нарушении ограничений БД
    """
    try:
        # Проверяем существование группы
        group = Groups.get(Groups.id == group_id)

        # Создаем студента
        student = Students.create(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            group_id=group_id,
            notes=notes,
            updated_at=datetime.datetime.now(),
        )

        return student

    except DoesNotExist:
        print(f"Группа с ID {group_id} не найдена.")
        raise
    except IntegrityError:
        print("Ошибка создания студента: нарушение ограничений БД.")
        raise


def update_student_by_id(student_id: int, **kwargs) -> Optional[Dict[str, Any]]:
    """
    Обновляет данные студента.

    Args:
        student_id: ID студента
        **kwargs: Поля для обновления (first_name, last_name, middle_name, group_id, notes)

    Returns:
        Словарь с обновленными данными студента или None если не найден

    Raises:
        DoesNotExist: Если студент или группа не найдены
        IntegrityError: При нарушении ограничений БД
    """
    try:
        student = Students.get(Students.id == student_id)

        # Если обновляется group_id, проверяем существование группы
        if "group_id" in kwargs:
            group = Groups.get(Groups.id == kwargs["group_id"])

        # Обновляем поля
        for field, value in kwargs.items():
            if hasattr(student, field):
                setattr(student, field, value)

        student.updated_at = datetime.datetime.now()
        student.save()

        return student

    except DoesNotExist:
        print(f"Студент с ID {student_id} не найден или указана несуществующая группа.")
        raise
    except IntegrityError:
        print("Ошибка обновления студента: нарушение ограничений БД.")
        raise


def delete_student_by_id(student_id: int) -> bool:
    """
    Удаляет студента по ID.
    """
    try:
        student = Students.get(Students.id == student_id)
        student.delete_instance()
        return True
    except DoesNotExist:
        print(f"Студент с ID {student_id} не найден.")
        raise
    except IntegrityError:
        print("Невозможно удалить студента, так как он связан с другими записями.")
        raise


def get_students_list(
    group_id: Optional[int] = None,
    name_filter: Optional[str] = None,
    sort_by: str = "last_name",
    sort_direction: str = "asc",
    expand_fields: Optional[List[str]] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> List[Students]:
    """
    Получает список студентов с возможностью фильтрации, сортировки и пагинации.

    Args:
        group_id: ID группы для фильтрации (опционально)
        name_filter: Фильтр по имени/фамилии (опционально)
        sort_by: Поле для сортировки ('last_name', 'first_name', 'created_at')
        sort_direction: Направление сортировки ('asc' или 'desc')
        expand_fields: Список полей для раскрытия связанных объектов (например, ['group'])
        limit: Лимит записей для пагинации (опционально)
        offset: Смещение для пагинации (опционально)

    Returns:
        Список словарей с данными студентов
    """
    try:
        # Создаем базовый запрос
        query = Students.select()

        # Добавляем JOIN для связанных таблиц, если нужно
        if expand_fields and "group" in expand_fields:
            query = query.join(Groups)

        # Применяем фильтр по группе
        if group_id is not None:
            query = query.where(Students.group_id == group_id)

        # Применяем фильтр по имени
        if name_filter:
            name_filter = name_filter.strip()
            query = query.where(
                (Students.first_name.contains(name_filter))
                | (Students.last_name.contains(name_filter))
                | (Students.middle_name.contains(name_filter))
            )

        # Применяем сортировку (Если поле не найдено, используем last_name по умолчанию)
        sort_field = getattr(Students, sort_by, Students.last_name)
        if sort_direction.lower() == "desc":
            query = query.order_by(sort_field.desc())
        else:
            query = query.order_by(sort_field.asc())

        # Применяем пагинацию
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)

        # Выполняем запрос и сериализуем результаты
        students = list(query)
        return students

    except Exception as e:
        print(f"Ошибка при получении списка студентов: {e}")
        raise


def get_students_by_group_name(
    group_name: str, expand_fields: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Получает список студентов по названию группы.

    Args:
        group_name: Название группы
        expand_fields: Список полей для раскрытия связанных объектов

    Returns:
        Список словарей с данными студентов
    """
    try:
        query = Students.select().join(Groups).where(Groups.group_name == group_name)
        query = query.order_by(Students.last_name.asc(), Students.first_name.asc())

        students = list(query)
        return students

    except DoesNotExist:
        print(f"Группа с названием '{group_name}' не найдена.")
        return []
    except Exception as e:
        print(f"Ошибка при получении студентов группы: {e}")
        raise
