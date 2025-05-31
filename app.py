"""
Flask приложение для работы с API "Academy"
"""

from flask import Flask, jsonify, request
from utils import get_group_by_id
from peewee import DoesNotExist, IntegrityError

# Создаем экземпляр Flask приложения
app = Flask(__name__)

# Конфигурация приложения - выключим ascii режим для поддержки кириллицы
app.config["JSON_AS_ASCII"] = False


# Делаем первый маршрут для добычи группы по ID 
# http://127.0.0.1:5000/group/1
@app.route("/group/<int:group_id>", methods=["GET"])
def get_group(group_id):
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
# Запуск приложения
if __name__ == "__main__":
    app.run(debug=True)
