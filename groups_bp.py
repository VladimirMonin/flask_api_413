from flask import request
from flask_restx import Namespace, Resource, fields
from peewee import DoesNotExist, IntegrityError
from utils import (
    get_group_by_id,
    get_groups_list,
    create_group,
    update_group_id,
    delete_group_id,
)
from http import HTTPStatus

# Создаем экземпляр Namespace для групп
groups_bp = Namespace("group", description="Операции с группами")

# Модель для ответа группы
group_model = groups_bp.model(
    "Group",
    {
        "id": fields.Integer(
            readonly=True, description="Уникальный идентификатор группы"
        ),
        "group_name": fields.String(required=True, description="Название группы"),
        "created_at": fields.DateTime(
            dt_format="rfc822", description="Дата создания группы"
        ),
    },
)

# Модель для входных данных при создании/обновлении группы
group_input_model = groups_bp.model(
    "GroupInput",
    {
        "group_name": fields.String(required=True, description="Название группы"),
    },
)


@groups_bp.route("/<int:group_id>")
@groups_bp.param("group_id", "Уникальный идентификатор группы")
@groups_bp.response(HTTPStatus.NOT_FOUND, "Группа не найдена")
@groups_bp.response(HTTPStatus.FORBIDDEN, "Доступ запрещен")
class GroupResource(Resource):
    @groups_bp.doc("get_group")
    @groups_bp.marshal_with(group_model)
    def get(self, group_id):
        """Получить информацию о группе по ID"""
        try:
            group = get_group_by_id(group_id)
            return group
        except DoesNotExist:
            groups_bp.abort(HTTPStatus.NOT_FOUND, "Группа не найдена")


@groups_bp.route("/list/")
@groups_bp.param(
    "sort_direction", "Направление сортировки (asc или desc)", default="asc"
)
@groups_bp.param("name_filter", "Фильтр по названию группы")
@groups_bp.response(HTTPStatus.BAD_REQUEST, "Неверное направление сортировки")
class GroupListResource(Resource):
    @groups_bp.doc("list_groups")
    @groups_bp.marshal_list_with(group_model)
    def get(self):
        """Получить список всех групп"""
        sort_direction = request.args.get("sort_direction", "asc")
        name_filter = request.args.get("name_filter")

        if sort_direction not in ["asc", "desc"]:
            groups_bp.abort(HTTPStatus.BAD_REQUEST, "Неверное направление сортировки")

        groups = get_groups_list(sort_direction, name_filter)
        return groups


@groups_bp.route("/create/")
@groups_bp.response(
    HTTPStatus.BAD_REQUEST, "Название группы обязательно или группа с таким названием уже существует"
)
class GroupCreateResource(Resource):
    @groups_bp.doc("create_group")
    @groups_bp.expect(group_input_model)
    @groups_bp.marshal_with(group_model, code=201)
    def post(self):
        """Создать новую группу"""
        data = groups_bp.payload
        group_name = data.get("group_name")

        if not group_name:
            groups_bp.abort(HTTPStatus.BAD_REQUEST, "Название группы обязательно")

        try:
            group = create_group(group_name)
            return group, HTTPStatus.CREATED
        except IntegrityError:
            groups_bp.abort(
                HTTPStatus.BAD_REQUEST, "Группа с таким названием уже существует"
            )


@groups_bp.route("/update/<int:group_id>")
@groups_bp.param("group_id", "Уникальный идентификатор группы")
@groups_bp.response(
    HTTPStatus.BAD_REQUEST, "Название группы обязательно или группа с таким названием уже существует"
)
@groups_bp.response(HTTPStatus.NOT_FOUND, "Группа не найдена")
class GroupUpdateResource(Resource):
    @groups_bp.doc("update_group")
    @groups_bp.expect(group_input_model)
    @groups_bp.marshal_with(group_model)
    def put(self, group_id):
        """Обновить информацию о группе"""
        data = groups_bp.payload
        group_name = data.get("group_name")

        if not group_name:
            groups_bp.abort(HTTPStatus.BAD_REQUEST, "Название группы обязательно")

        try:
            updated_group = update_group_id(group_id, group_name)
            return updated_group
        except DoesNotExist:
            groups_bp.abort(HTTPStatus.NOT_FOUND, "Группа не найдена")
        except IntegrityError:
            groups_bp.abort(
                HTTPStatus.BAD_REQUEST, "Группа с таким названием уже существует"
            )


@groups_bp.route("/delete/<int:group_id>")
@groups_bp.param("group_id", "Уникальный идентификатор группы")
@groups_bp.response(HTTPStatus.NO_CONTENT, "Группа успешно удалена")
@groups_bp.response(HTTPStatus.NOT_FOUND, "Группа не найдена")
class GroupDeleteResource(Resource):
    @groups_bp.doc("delete_group")
    def delete(self, group_id):
        """Удалить группу по ID"""
        try:
            delete_group_id(group_id)
            return "", HTTPStatus.NO_CONTENT
        except DoesNotExist:
            groups_bp.abort(HTTPStatus.NOT_FOUND, "Группа не найдена")
