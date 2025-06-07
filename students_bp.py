from flask_restx import Namespace, Resource, fields
from peewee import DoesNotExist
from utils import get_student_by_id, create_student
from http import HTTPStatus

# Создаем экземпляр Namespace для студентов
students_bp = Namespace("student", description="Операции со студентами")

# Модель для ответа студента
student_model = students_bp.model(
    "Student",
    {
        "id": fields.Integer(readonly=True, description="Уникальный идентификатор студента"),
        "first_name": fields.String(required=True, description="Имя студента"),
        "middle_name": fields.String(description="Отчество студента"),
        "last_name": fields.String(required=True, description="Фамилия студента"),
        "group_id": fields.Integer(required=True, description="ID группы"),
        "group_name": fields.String(attribute="group_id.group_name", description="Название группы"),
        "notes": fields.String(description="Заметки о студенте"),
        "created_at": fields.DateTime(dt_format="rfc822", description="Дата создания записи"),
    },
)

# Модель для входных данных при создании студента
student_input_model = students_bp.model(
    "StudentInput",
    {
        "first_name": fields.String(required=True, description="Имя студента"),
        "middle_name": fields.String(description="Отчество студента"),
        "last_name": fields.String(required=True, description="Фамилия студента"),
        "group_id": fields.Integer(required=True, description="ID группы"),
        "notes": fields.String(description="Заметки о студенте"),
    },
)


@students_bp.route("/<int:student_id>")
@students_bp.param("student_id", "Уникальный идентификатор студента")
@students_bp.response(HTTPStatus.NOT_FOUND, "Студент не найден")
class StudentResource(Resource):
    @students_bp.doc("get_student")
    @students_bp.marshal_with(student_model)
    def get(self, student_id):
        """Получить информацию о студенте по ID"""
        try:
            student = get_student_by_id(student_id, expand_fields=['group'])
            if student is None:
                 students_bp.abort(HTTPStatus.NOT_FOUND, "Студент не найден")
            return student
        except DoesNotExist:
            students_bp.abort(HTTPStatus.NOT_FOUND, "Студент не найден")


@students_bp.route("/create/")
@students_bp.response(HTTPStatus.CREATED, "Студент успешно создан", student_model)
@students_bp.response(HTTPStatus.BAD_REQUEST, "Неверные данные")
@students_bp.response(HTTPStatus.NOT_FOUND, "Группа не найдена")
class StudentCreateResource(Resource):
    @students_bp.doc("create_student")
    @students_bp.expect(student_input_model)
    @students_bp.marshal_with(student_model, code=HTTPStatus.CREATED)
    def post(self):
        """Создать нового студента"""
        data = students_bp.payload
        
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        group_id = data.get("group_id")

        if not first_name or not last_name or not group_id:
            students_bp.abort(HTTPStatus.BAD_REQUEST, "Имя, фамилия и ID группы обязательны")

        try:
            student = create_student(
                first_name=first_name,
                last_name=last_name,
                group_id=group_id,
                middle_name=data.get("middle_name"),
                notes=data.get("notes"),
            )
            return student, HTTPStatus.CREATED
        except DoesNotExist:
            students_bp.abort(HTTPStatus.NOT_FOUND, "Группа не найдена")
        except Exception as e:
            students_bp.abort(HTTPStatus.BAD_REQUEST, str(e))
