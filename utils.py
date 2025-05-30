from sqlite3 import IntegrityError
from models import Groups, Students
from peewee import DoesNotExist, IntegrityError
import json
import datetime
from typing import Optional


# Как бы могла выглядить функция для сериализации в JSON одного объекта с неопределенным количеством полей?
def serialize_model_instance(instance):
    """
    Сериализует объект модели в словарь, включая только определенные поля.
    """
    serialized_data = {}

    # _meta.sorted_fields позволяет получить все поля модели в порядке их определения
    for field in instance._meta.sorted_fields:
        field_data = getattr(instance, field.name)

        # Проверяем если данные являются объектом даты или времени- превращаем их в строку
        if isinstance(field_data, (datetime.date, datetime.datetime)):
            serialized_data[field.name] = field_data.isoformat()
        else:
            serialized_data[field.name] = field_data

    json_data = json.dumps(serialized_data, indent=4, ensure_ascii=False)
    return json_data



def get_group_by_id(group_id: int) -> Optional[Groups]:
    """
    Получает группу по ID.
    """
    try:
        group = Groups.get(Groups.id == group_id)
        return group
    except DoesNotExist:
        return None

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

def delete_group_by_id(group_id: int) -> bool:
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

def update_group_by_id(group_id: int, new_group_name: str) -> Optional[Groups]:
    """
    Обновляет имя группы по ID.
    """
    try:
        group = Groups.get(Groups.id == group_id)
        group.group_name = new_group_name
        group.save()
        return group
    except DoesNotExist:
        print("Группа не найдена.")
        raise
    except IntegrityError:
        print("Невозможно обновить группу, так как новое имя уже существует.")
        raise



def get_groups_list(sort_direction: str = 'asc', name_filter: Optional[str] = None) -> list:
    """
    Получает список групп с возможностью сортировки и фильтрации по имени.
    """
    query = Groups.select()

    if name_filter:
        query = query.where(Groups.group_name.contains(name_filter))

    if sort_direction == 'asc':
        query = query.order_by(Groups.group_name.asc())
    elif sort_direction == 'desc':
        query = query.order_by(Groups.group_name.desc())

    return list(query)


# Протестируем список групп
if __name__ == "__main__":
    groups = get_groups_list(sort_direction='asc', name_filter='python')
    if groups:
        print("Список групп:")
        for group in groups:
            print(serialize_model_instance(group))
    else:
        print("Группы не найдены.")


#################### СТУДЕНТЫ ####################

def create_student(first_name: str, middle_name: Optional[str], last_name: str, group_id: int, notes: Optional[str] = None) -> Students:
    # 1. Создание студента
    student = Students.create(
        first_name=first_name,
        middle_name=middle_name,
        last_name=last_name,
        group_id=group_id,
        notes=notes
    )

    # 2. Возвращаем экземпляр студента
    return student


def get_student_by_id(student_id: int) -> Optional[Students]:
    """
    Получает студента по ID.
    """
    try:
        student = Students.get(Students.id == student_id)
        return student
    except DoesNotExist:
        print("Студент не найден.")
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
        print("Студент не найден.")
        raise
    except IntegrityError:
        print("Невозможно удалить студента, так как он связан с другими записями.")
        raise


def update_student_by_id(**kwargs) -> Optional[Students]:
    # 1. берем модель и проверяем что в кваргах есть все поля (кроме created_at updated_at)
    required_fields = ['id', 'first_name', 'last_name', 'group_id', 'notes']
    
    if not all(field in kwargs for field in required_fields):
        raise ValueError("Отсутствуют обязательные поля для обновления студента.")
    
    # 2. Получаем студента по ID
    student_id = kwargs.pop('id')

    try:
        student = Students.get(Students.id == student_id)
        
        # 3. Обновляем поля студента
        student.update(**kwargs)

        student.save()
        return student
    
    except DoesNotExist:
        print("Студент не найден.")
        raise

def get_students_list(sort_direction: str = 'asc', group_filter: Optional[str] = None) -> list:
    """
    Получает список студентов с возможностью сортировки и фильтрации по названию группы.
    """
    query = Students.select().join(Groups)

    if group_filter:
        query = query.where(Groups.group_name.contains(group_filter))

    if sort_direction == 'asc':
        query = query.order_by(Students.last_name.asc())
    elif sort_direction == 'desc':
        query = query.order_by(Students.last_name.desc())

    return list(query)


# Протестируем добычу студентов
if __name__ == "__main__":
    students = get_students_list(sort_direction='asc', group_filter='413')
    if students:
        print("Список студентов:")
        for student in students:
            print(student)
    else:
        print("Студенты не найдены.")