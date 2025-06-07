from utils import get_group_by_id, get_groups_list, create_group, update_group_id, delete_group_id
from flask import Blueprint, jsonify, request
from peewee import DoesNotExist, IntegrityError
from utils import check_access

# Создаем экземпляр Blueprint
# url_prefix='/group' - префикс для всех маршрутов в этом Blueprint
# Например мы пишем маршрут /<int:group_id>, а он будет доступен по адресу /group/<int:group_id/
groups_bp = Blueprint('groups', __name__, url_prefix='/group')


@groups_bp.route("/<int:group_id>", methods=["GET"])
def get_group(group_id):
    
    # Проверяем доступ пользователя
    if not check_access(request, "user"):
        return jsonify({"error": "Доступ запрещен"}), 403
    
    try:
        group = get_group_by_id(group_id)
    
    except DoesNotExist:
        return jsonify({"error": "Группа не найдена"}), 404
    
    else:
        group_dict = {
            "id": group.id,
            "group_name": group.group_name,
            "created_at": group.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        return jsonify(group_dict), 200
    
@groups_bp.route("/list/", methods=["GET"])
def list_groups():
    
    # Пробуем добыть параметры из URL запроса
    sort_direction = request.args.get("sort_direction", "asc")
    name_filter = request.args.get("name_filter")
    
    if sort_direction not in ["asc", "desc"]:
        return jsonify({"error": "Неверное направление сортировки"}), 400
    
    groups = get_groups_list(sort_direction, name_filter)

    groups_list = []
    for group in groups:
        group_dict = {
            "id": group.id,
            "group_name": group.group_name,
            "created_at": group.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
        groups_list.append(group_dict)

    return jsonify(groups_list), 200


# create_group
@groups_bp.route("/create/", methods=["POST"])
def group_create():
    # Получаем данные из запроса
    data = request.get_json()
    group_name = data.get("group_name")

    if not group_name:
        return jsonify({"error": "Название группы обязательно"}), 400

    try:
        group = create_group(group_name)  # Предполагается, что функция создает группу в БД
    except IntegrityError:
        return jsonify({"error": "Группа с таким названием уже существует"}), 400

    group_dict = {
        "id": group.id,
        "group_name": group.group_name,
        "created_at": group.created_at.strftime("%Y-%m-%d %H:%M:%S"),
    }

    return jsonify(group_dict), 201

@groups_bp.route("/update/<int:group_id>", methods=["PUT"])
def update_group(group_id):
    # Получаем данные из запроса
    data = request.get_json()
    group_name = data.get("group_name")

    if not group_name:
        return jsonify({"error": "Название группы обязательно"}), 400

    try:
        updated_group = update_group_id(group_id, group_name)

    except DoesNotExist:
        return jsonify({"error": "Группа не найдена"}), 404
    
    except IntegrityError:
        return jsonify({"error": "Группа с таким названием уже существует"}), 400

    group_dict = {
        "id": updated_group.id,
        "group_name": updated_group.group_name,
        "created_at": updated_group.created_at.strftime("%Y-%m-%d %H:%M:%S"),
    }

    return jsonify(group_dict), 200

@groups_bp.route("/delete/<int:group_id>", methods=["DELETE"])
def delete_group(group_id):
    try:
        delete_group_id(group_id)  # Предполагается, что функция удаляет группу по ID

    except DoesNotExist:
        return jsonify({"error": "Группа не найдена"}), 404
    
    return jsonify({"message": "Группа успешно удалена"}), 200