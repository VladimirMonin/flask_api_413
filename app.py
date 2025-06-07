"""
Flask приложение для работы с API "Academy"
"""

from flask import Flask, jsonify, request
from utils import get_group_by_id, get_groups_list, get_student_by_id, create_group, update_group_id, delete_group_id, create_student
from peewee import DoesNotExist, IntegrityError
from groups_bp import groups_bp
from students_bp import students_bp

# Создаем экземпляр Flask приложения
app = Flask(__name__)

# Конфигурация приложения - выключим ascii режим для поддержки кириллицы
app.config["JSON_AS_ASCII"] = False

# Регистрация Blueprint
app.register_blueprint(groups_bp)
app.register_blueprint(students_bp)


# Запуск приложения
if __name__ == "__main__":
    app.run(debug=True)
