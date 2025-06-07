"""
Flask приложение для работы с API "Academy"
"""

from flask import Flask
from flask_restx import Api
from groups_bp import groups_bp
from students_bp import students_bp

# Создаем экземпляр Flask приложения
app = Flask(__name__)

# Конфигурация приложения - выключим ascii режим для поддержки кириллицы
app.config["JSON_AS_ASCII"] = False

# Определение авторизации для Swagger UI
authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API-KEY'
    }
}

# Создаем экземпляр Flask-RESTX Api
api = Api(app, version='1.0', title='Academy API',
          description='API для управления группами и студентами в академии',
          authorizations=authorizations,
          security='apikey')

# Регистрация Blueprint'ов как Namespaces в Flask-RESTX
api.add_namespace(groups_bp)
api.add_namespace(students_bp)


# Запуск приложения
if __name__ == "__main__":
    app.run(debug=True)
