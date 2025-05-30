from sqlite3 import IntegrityError
from models import Groups, Students
from peewee import DoesNotExist, IntegrityError
import json
import datetime
from typing import Optional, List, Dict, Any


# Улучшенная функция сериализации с поддержкой expand для связанных объектов
def serialize_model_instance(instance, expand_fields: Optional[List[str]] = None):
    """
    Сериализует объект модели в словарь, включая только определенные поля.
    
    Args:
        instance: Экземпляр модели для сериализации
        expand_fields: Список полей для раскрытия связанных объектов (например, ['group'])
    """
    serialized_data = {}
    expand_fields = expand_fields or []

    # _meta.sorted_fields позволяет получить все поля модели в порядке их определения
    for field in instance._meta.sorted_fields:
        field_data = getattr(instance, field.name)

        # Проверяем если это ForeignKey и нужно его раскрыть
        # rel_model - это модель, на которую ссылается ForeignKey
        if hasattr(field, 'rel_model') and field.name.replace('_id', '') in expand_fields:
            # Получаем связанный объект
            related_field_name = field.name.replace('_id', '')
            if hasattr(instance, related_field_name):
                related_object = getattr(instance, related_field_name)
                serialized_data[related_field_name] = serialize_model_instance(related_object)
            continue

        # Проверяем если данные являются объектом даты или времени - превращаем их в строку
        if isinstance(field_data, (datetime.date, datetime.datetime)):
            serialized_data[field.name] = field_data.isoformat()
        else:
            serialized_data[field.name] = field_data

    return serialized_data


def serialize_to_json(instance, expand_fields: Optional[List[str]] = None):
    """
    Сериализует объект модели в JSON строку.
    """
    serialized_data = serialize_model_instance(instance, expand_fields)
    return json.dumps(serialized_data, indent=4, ensure_ascii=False)

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


# ========== ФУНКЦИИ ДЛЯ РАБОТЫ СО СТУДЕНТАМИ ==========

def get_student_by_id(student_id: int, expand_fields: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
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
        if expand_fields and 'group' in expand_fields:
            query = query.join(Groups)
        
        student = query.where(Students.id == student_id).get()
        return serialize_model_instance(student, expand_fields)
    except DoesNotExist:
        return None


def create_student(first_name: str, last_name: str, group_id: int, 
                  middle_name: Optional[str] = None, notes: Optional[str] = None) -> Dict[str, Any]:
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
            updated_at=datetime.datetime.now()
        )
        
        return serialize_model_instance(student)
        
    except DoesNotExist:
        print(f"Группа с ID {group_id} не найдена.")
        raise
    except IntegrityError:
        print("Ошибка создания студента: нарушение ограничений БД.")
        raise


def update_student(student_id: int, **kwargs) -> Optional[Dict[str, Any]]:
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
        if 'group_id' in kwargs:
            group = Groups.get(Groups.id == kwargs['group_id'])
        
        # Обновляем поля
        for field, value in kwargs.items():
            if hasattr(student, field):
                setattr(student, field, value)
        
        student.updated_at = datetime.datetime.now()
        student.save()
        
        return serialize_model_instance(student)
        
    except DoesNotExist:
        print(f"Студент с ID {student_id} не найден или указана несуществующая группа.")
        raise
    except IntegrityError: