from models import Groups
from peewee import DoesNotExist
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


# Протестируем на группе 1
if __name__ == "__main__":
    group = get_group_by_id(1)
    if group:
        print("Группа найдена:\n", serialize_model_instance(group))
    else:
        print("Группа не найдена.")
