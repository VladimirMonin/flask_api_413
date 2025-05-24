"""
Структрура базы данных для ORM

"""

from peewee import *
import datetime

db = SqliteDatabase("academy_orm.db")


# Группы
class Groups(Model):
    group_name = CharField(unique=True, null=False, max_length=50)
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db


# Таблица students
class Students(Model):
    first_name = CharField(max_length=50)
    middle_name = CharField(null=True, max_length=50)
    last_name = CharField(max_length=50)
    group_id = ForeignKeyField(Groups, backref="students", on_delete="RESTRICT")
    notes = TextField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db
        indexes = (
            (("group_id",), False),
            (("last_name",), False),
        )


# Онлайн занятия
class OnlineLessons(Model):
    group_id = ForeignKeyField(Groups, backref="online_lessons", on_delete="RESTRICT")
    lesson_date = DateField(default=datetime.date.today)
    lesson_time = TimeField(default=datetime.datetime.now)
    academic_hours = IntegerField(default=2)
    telegram_record_link = CharField(null=True, max_length=300)
    lesson_theme = CharField(max_length=200)
    lesson_notes = TextField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db
        indexes = (
            (("group_id",), False),
            (("lesson_date",), False),
        )
        constraints = [Check("academic_hours > 0 AND academic_hours <= 8")]


# Таблица для отметки присутствия студентов на занятиях Many-to-Many
class StudentsOnlineLessons(Model):
    student_id = ForeignKeyField(
        Students, backref="students_online_lessons", on_delete="CASCADE"
    )
    online_lesson_id = ForeignKeyField(
        OnlineLessons, backref="students_online_lessons", on_delete="CASCADE"
    )
    mark = IntegerField(default=6)
    is_active = BooleanField(default=False)
    attendance_notes = TextField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db
        indexes = (
            (("student_id",), False),
            (("online_lesson_id",), False),
        )
        constraints = [
            Check("mark >= 1 AND mark <= 12"),
            Check("is_active IN (0, 1)"),
            SQL("UNIQUE(student_id, online_lesson_id)"),
        ]


# homeworks - таблица с текстом выданных домашних заданий
class Homeworks(Model):
    online_lesson_id = ForeignKeyField(
        OnlineLessons, backref="homeworks", on_delete="CASCADE"
    )
    summary = TextField()
    homework_text = TextField()
    homework_date = DateField(default=datetime.date.today)
    deadline_date = DateField(constraints=[SQL("DEFAULT DATE('now', '+7 days')")])
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db
        constraints = [
            Check("is_active IN (0, 1)"),
            Check("deadline_date >= homework_date"),
        ]


# homeworks_students - таблица для отметки выполнения домашних заданий
class HomeworksStudents(Model):
    student_id = ForeignKeyField(
        Students, backref="homeworks_students", on_delete="CASCADE"
    )
    homework_id = ForeignKeyField(
        Homeworks, backref="homeworks_students", on_delete="CASCADE"
    )

    homework_text = TextField()
    file_path = CharField(null=True, max_length=400)

    status = CharField(
        # Первый элемент - то что будет храниться в базе, второй - то что будет отображаться в интерфейсе
        choices=[
            ("не сдано", "не сдано"),
            ("принято", "принято"),
            ("проверено", "проверено"),
            ("обратная связь выдана", "обратная связь выдана"),
        ]
    )
    mark = IntegerField(null=True)
    submission_date = DateTimeField(default=datetime.datetime.now)
    checked_date = DateTimeField(null=True)
    feedback_text = TextField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db
        indexes = ((("homework_id", "student_id"), True),)

        constraints = [
            Check("mark IS NULL OR (mark >= 1 AND mark <= 12)"),
            # TODO - Убрать нафиг
            SQL("UNIQUE(student_id, homework_id)"),
        ]


# students_reviews - таблица для обратной связи на студента
class StudentsReviews(Model):
    student_id = ForeignKeyField(
        Students, backref="students_reviews", on_delete="CASCADE"
    )
    review_text = TextField()
    review_date = DateField(default=datetime.date.today)
    review_start_date = DateField()
    review_end_date = DateField()
    is_published = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db
        indexes = ((("student_id",), False),)

        constraints = [
            Check("is_published IN (0, 1)"),
            Check("review_end_date IS NULL OR review_end_date >= review_start_date"),
        ]
