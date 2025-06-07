from utils import  get_student_by_id, create_student
from flask import Blueprint, jsonify, request
from peewee import DoesNotExist, IntegrityError

# Создаем экземпляр Blueprint
students_bp = Blueprint('students', __name__, url_prefix='/student')


# Добыть студента по ID
@students_bp.route("/<int:student_id>", methods=["GET"])
def get_student(student_id):
    try:
        student = get_student_by_id(student_id)  # Предполагается, что функция работает с ID студента

    except DoesNotExist:
        return jsonify({"error": "Студент не найден"}), 404
    
    else:
        student_dict = {
            "id": student.id,
            "first_name": student.first_name,
            "middle_name": student.middle_name,
            "last_name": student.last_name,
            "group_id": student.group_id.id,
            "group_name": student.group_id.group_name,
            "created_at": student.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        return jsonify(student_dict), 200
    
# Создание студента
@students_bp.route("/create/", methods=["POST"])
def student_create():
    # Получаем данные из запроса
    data = request.get_json()
    
    # Получаем необходимые поля из JSON
    first_name = data.get("first_name")
    middle_name = data.get("middle_name")
    last_name = data.get("last_name")
    group_id = data.get("group_id")
    notes = data.get("notes")

    if not first_name or not last_name or not group_id:
        return jsonify({"error": "Имя, фамилия и ID группы обязательны"}), 400

    try:
        student = create_student(first_name, last_name, group_id, middle_name, notes)  # Предполагается, что функция создает студента в БД
    except DoesNotExist:
        return jsonify({"error": "Группа не найдена"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    student_dict = {
        "id": student.id,
        "first_name": student.first_name,
        "middle_name": student.middle_name,
        "last_name": student.last_name,
        "group_id": student.group_id.id,
        "group_name": student.group_id.group_name,
        "notes": student.notes,
        "created_at": student.created_at.strftime("%Y-%m-%d %H:%M:%S"),
    }

    return jsonify(student_dict), 201
