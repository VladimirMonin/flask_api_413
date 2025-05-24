# Анализ моделей Peewee на соответствие SQL структуре

## Общий анализ

Найдена документация по Peewee ORM в Context7. Выполняю поэтапную проверку каждой модели на соответствие SQL структуре из lesson_43.sql.

## 1. Модель Groups

### SQL структура

```sql
CREATE TABLE groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_name TEXT NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Peewee модель

```python
class Groups(Model):
    group_name = CharField(unique=True, null=False, max_length=50)
    created_at = DateTimeField(constraints=[SQL("CURRENT_TIMESTAMP")])
```

### Проблемы

1. ❌ Отсутствует primary key (id) - по умолчанию Peewee создаст AutoField(id), что корректно
# TODO - Менять!
2. ❌ `constraints=[SQL("CURRENT_TIMESTAMP")]` неправильно - нужно `default` или `constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")]`
3. ✅ `group_name` корректно определен как CharField с unique=True
4. ❌ Отсутствует обновление `updated_at` из SQL (SQL имеет триггер для updated_at)

### Рекомендации

- Исправить default для created_at
- Добавить updated_at поле

## 2. Модель Students

### SQL структура

```sql
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    middle_name TEXT,
    last_name TEXT NOT NULL,
    group_id INTEGER NOT NULL,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE RESTRICT
);
```

### Peewee модель

```python
class Students(Model):
    first_name = CharField(max_length=50)
    middle_name = CharField(null=True, max_length=50)
    last_name = CharField(max_length=50)
    group_id = ForeignKeyField(Groups, backref="students", on_delete="RESTRICT")
    notes = TextField(null=True)
    created_at = DateTimeField(constraints=[SQL("CURRENT_TIMESTAMP")])
    updated_at = DateTimeField(constraints=[SQL("CURRENT_TIMESTAMP")])
```

### Проблемы

1. ❌ `first_name` и `last_name` должны быть `null=False` (NOT NULL в SQL)
2. ❌ `constraints=[SQL("CURRENT_TIMESTAMP")]` неправильно для default значений
3. ✅ ForeignKeyField корректно настроен с on_delete="RESTRICT"
4. ✅ Индексы правильно определены в Meta класс
5. ✅ TextField для notes корректен

### Рекомендации

- Добавить null=False для обязательных полей
- Исправить default для timestamp полей

## 3. Модель OnlineLessons

### SQL структура

```sql
CREATE TABLE online_lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    lesson_date DATE DEFAULT (DATE ('now')),
    lesson_time TIME DEFAULT (TIME('now')),
    academic_hours INTEGER DEFAULT 2,
    telegram_record_link TEXT DEFAULT NULL,
    lesson_theme TEXT NOT NULL,
    lesson_notes TEXT DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE RESTRICT,
    CHECK (academic_hours > 0 AND academic_hours <= 8)
);
```

### Peewee модель

```python
class OnlineLessons(Model):
    group_id = ForeignKeyField(Groups, backref="online_lessons", on_delete="RESTRICT")
    lesson_date = DateField(constraints=[SQL("DATE('now')")])
    lesson_time = TimeField(constraints=[SQL("TIME('now')")])
    academic_hours = IntegerField(default=2)
    telegram_record_link = CharField(null=True, max_length=300)
    lesson_theme = CharField(max_length=200)
    lesson_notes = TextField(null=True)
    created_at = DateTimeField(constraints=[SQL("CURRENT_TIMESTAMP")])
    updated_at = DateTimeField(constraints=[SQL("CURRENT_TIMESTAMP")])
```

### Проблемы

1. ❌ `lesson_theme` должно быть `null=False` (NOT NULL в SQL)
2. ❌ Неправильно использованы constraints для default значений
3. ✅ Check constraint правильно определен в Meta
4. ✅ ForeignKeyField корректен
5. ✅ Индексы правильно определены

### Рекомендации

- Исправить default значения для дат
- Добавить null=False для lesson_theme

## 4. Модель StudentsOnlineLessons

### SQL структура

```sql
CREATE TABLE students_online_lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    online_lesson_id INTEGER NOT NULL,
    mark INTEGER DEFAULT 6,
    is_active INTEGER DEFAULT 0,
    attendance_notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
    FOREIGN KEY (online_lesson_id) REFERENCES online_lessons (id) ON DELETE CASCADE,
    CHECK (mark >= 1 AND mark <= 12),
    CHECK (is_active IN (0, 1)),
    UNIQUE (student_id, online_lesson_id)
);
```

### Peewee модель

```python
class StudentsOnlineLessons(Model):
    student_id = ForeignKeyField(Students, backref="students_online_lessons", on_delete="CASCADE")
    online_lesson_id = ForeignKeyField(OnlineLessons, backref="students_online_lessons", on_delete="CASCADE")
    mark = IntegerField(default=6)
    is_active = BooleanField(default=False)
    attendance_notes = TextField(null=True)
    created_at = DateTimeField(constraints=[SQL("CURRENT_TIMESTAMP")])
    updated_at = DateTimeField(constraints=[SQL("CURRENT_TIMESTAMP")])
```

### Проблемы

1. ❌ `is_active` как BooleanField не соответствует SQL INTEGER DEFAULT 0
2. ❌ Неправильные constraints для timestamp полей
3. ❌ Check для is_active дублирует BooleanField логику
4. ✅ ForeignKeyField корректно настроены
5. ✅ Unique constraint правильно определен
6. ✅ Check constraint для mark корректен

### Рекомендации

- Заменить BooleanField на IntegerField для is_active
- Исправить default значения

## 5. Модель Homeworks

### SQL структура

```sql
CREATE TABLE homeworks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    online_lesson_id INTEGER NOT NULL,
    summary TEXT NOT NULL,
    homework_text TEXT NOT NULL,
    homework_date DATE DEFAULT (DATE ('now')),
    deadline_date DATE DEFAULT (DATE ('now', '+7 days')),
    is_active INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (online_lesson_id) REFERENCES online_lessons (id) ON DELETE CASCADE,
    CHECK (is_active IN (0, 1)),
    CHECK (deadline_date >= homework_date)
);
```

### Peewee модель

```python
class Homeworks(Model):
    online_lesson_id = ForeignKeyField(OnlineLessons, backref="homeworks", on_delete="CASCADE")
    summary = TextField()
    homework_text = TextField()
    homework_date = DateField(constraints=[SQL("DATE('now')")])
    deadline_date = DateField(constraints=[SQL("DATE('now', '+7 days')")])
    is_active = BooleanField(default=True)
    created_at = DateTimeField(constraints=[SQL("CURRENT_TIMESTAMP")])
    updated_at = DateTimeField(constraints=[SQL("CURRENT_TIMESTAMP")])
```

### Проблемы

1. ❌ `summary` и `homework_text` должны быть `null=False` (NOT NULL в SQL)
2. ❌ Неправильные constraints для default значений
3. ❌ `is_active` как BooleanField не соответствует SQL INTEGER DEFAULT 1
4. ✅ ForeignKeyField правильно настроен
5. ✅ Check constraints корректны

### Рекомендации

- Добавить null=False для обязательных полей
- Заменить BooleanField на IntegerField для is_active
- Исправить default значения

## 6. Модель HomeworksStudents

### SQL структура

```sql
CREATE TABLE homeworks_students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    homework_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    uploaded_homework TEXT,
    status ENUM('completed', 'not_completed', 'in_process', 'marked_for_check') DEFAULT 'not_completed',
    mark INTEGER,
    is_published INTEGER DEFAULT 0,
    uploaded_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (homework_id) REFERENCES homeworks (id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
    CHECK (mark >= 1 AND mark <= 12),
    CHECK (is_published IN (0, 1)),
    UNIQUE (homework_id, student_id)
);
```

### Peewee модель

```python
class HomeworksStudents(Model):
    homework_id = ForeignKeyField(Homeworks, backref="homeworks_students", on_delete="CASCADE")
    student_id = ForeignKeyField(Students, backref="homeworks_students", on_delete="CASCADE")
    uploaded_homework = TextField(null=True)
    status = CharField(max_length=50, choices=[
        ('completed', 'Completed'),
        ('not_completed', 'Not Completed'),
        ('in_process', 'In Process'),
        ('marked_for_check', 'Marked for Check')
    ], default='not_completed')
    mark = IntegerField(null=True)
    is_published = BooleanField(default=False)
    uploaded_at = DateTimeField(null=True)
    created_at = DateTimeField(constraints=[SQL("CURRENT_TIMESTAMP")])
    updated_at = DateTimeField(constraints=[SQL("CURRENT_TIMESTAMP")])
```

### Проблемы

1. ❌ `is_published` как BooleanField не соответствует SQL INTEGER DEFAULT 0
2. ❌ Неправильные constraints для timestamp полей
3. ✅ Choices для status корректны
4. ✅ ForeignKeyField правильно настроены
5. ✅ Unique constraint определен корректно

### Рекомендации

- Заменить BooleanField на IntegerField для is_published
- Исправить default значения для timestamp полей

## 7. Модель StudentsReviews

### SQL структура

```sql
CREATE TABLE students_reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    homework_student_id INTEGER NOT NULL,
    teacher_note TEXT NOT NULL,
    mark INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (homework_student_id) REFERENCES homeworks_students (id) ON DELETE CASCADE,
    CHECK (mark >= 1 AND mark <= 12)
);
```

### Peewee модель

```python
class StudentsReviews(Model):
    homework_student_id = ForeignKeyField(HomeworksStudents, backref="students_reviews", on_delete="CASCADE")
    teacher_note = TextField()
    mark = IntegerField()
    created_at = DateTimeField(constraints=[SQL("CURRENT_TIMESTAMP")])
    updated_at = DateTimeField(constraints=[SQL("CURRENT_TIMESTAMP")])
```

### Проблемы

1. ❌ `teacher_note` и `mark` должны быть `null=False` (NOT NULL в SQL)
2. ❌ Неправильные constraints для timestamp полей
3. ✅ ForeignKeyField корректен
4. ✅ Check constraint для mark определен правильно

### Рекомендации

- Добавить null=False для обязательных полей
- Исправить default значения

---

## Анализ документации PeeWee из Context7

### 1. Правильное обозначение constraints с CURRENT_TIMESTAMP

Нашел в Context7, что в PeeWee есть два способа установки значений по умолчанию для даты и времени:

**Правильные способы:**

1. **Python default функция**: `default=datetime.datetime.now` - вызывается на уровне Python при создании объекта
2. **SQL constraints с DEFAULT**: `constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")]` - выполняется на уровне базы данных

**Неправильно в моделях (текущая проблема):**

```python
created_at = DateTimeField(constraints=[SQL("CURRENT_TIMESTAMP")])  # Неправильно!
```

**Правильно должно быть:**

```python
# Вариант 1: Python уровень
created_at = DateTimeField(default=datetime.datetime.now)

# Вариант 2: База данных уровень  
created_at = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")])

# Для SQLite еще один вариант:
created_at = DateTimeField(constraints=[SQL("DEFAULT (datetime('now'))")])
```

### 2. Поведение BooleanField в SQLite

Нашел в Context7, что:

- **BooleanField в PeeWee** автоматически мапится в SQLite как INTEGER со значениями 0 (False) и 1 (True)
- **Автоматическое преобразование**: PeeWee автоматически конвертирует Python bool значения в 0/1 для SQLite
- **Совместимость**: BooleanField полностью совместим с INTEGER DEFAULT 0/1 в SQLite

**Вывод**: Использование BooleanField в моделях **КОРРЕКТНО** для полей is_active и is_published, даже если в SQL они определены как INTEGER DEFAULT 0/1.

### 3. Значения null=False по умолчанию в полях

Нашел в Context7, что:

- **По умолчанию все поля в PeeWee**: `null=False` (NOT NULL)
- **Исключения**: Только ForeignKeyField по умолчанию имеет `null=True`
- **Явное указание**: Рекомендуется явно указывать `null=False` для обязательных полей для ясности кода

**Цитата из документации:**
"Field instances describe the mapping of Model attributes to database columns. If no field is initialized with primary_key=True, an auto-incrementing primary key named 'id' is automatically created. Fields are defined as class attributes... For non-null fields you must specify a default value."
3. ❌ `is_active` как BooleanField не соответствует SQL INTEGER
4. ✅ ForeignKeyField корректен
5. ✅ Check constraints правильно определены

### Рекомендации

- Добавить null=False для обязательных полей
- Заменить BooleanField на IntegerField для is_active
- Исправить default значения

## 6. Модель HomeworksStudents

### SQL структура

```sql
CREATE TABLE homeworks_students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    homework_id INTEGER NOT NULL,
    homework_text TEXT NOT NULL,
    file_path TEXT,
    status TEXT DEFAULT 'отправлено' CHECK (status IN (...)),
    mark INTEGER,
    submission_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    checked_date DATETIME,
    feedback_text TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
    FOREIGN KEY (homework_id) REFERENCES homeworks (id) ON DELETE CASCADE,
    CHECK (mark IS NULL OR (mark >= 1 AND mark <= 12)),
    UNIQUE (student_id, homework_id)
);
```

### Peewee модель

```python
class HomeworksStudents(Model):
    student_id = ForeignKeyField(Students, backref="homeworks_students", on_delete="CASCADE")
    homework_id = ForeignKeyField(Homeworks, backref="homeworks_students", on_delete="CASCADE")
    homework_text = TextField()
    file_path = CharField(null=True, max_length=400)
    status = CharField(choices=[...])
    mark = IntegerField(null=True)
    submission_date = DateTimeField(constraints=[SQL("CURRENT_TIMESTAMP")])
    checked_date = DateTimeField(null=True)
    feedback_text = TextField(null=True)
    created_at = DateTimeField(constraints=[SQL("CURRENT_TIMESTAMP")])
    updated_at = DateTimeField(constraints=[SQL("CURRENT_TIMESTAMP")])
```

### Проблемы

1. ❌ `homework_text` должно быть `null=False` (NOT NULL в SQL)
2. ❌ Отсутствует default='отправлено' для status
3. ❌ Неправильные constraints для timestamp полей
4. ❌ choices в status не соответствует полному списку из SQL
5. ✅ ForeignKeyField корректно настроены
6. ✅ Check constraints и unique правильно определены

### Рекомендации

- Добавить null=False для homework_text
- Добавить default для status
- Исправить список choices
- Исправить default значения

## 7. Модель StudentsReviews

### SQL структура

```sql
CREATE TABLE students_reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    review_text TEXT NOT NULL,
    review_date DATE DEFAULT (DATE ('now')),
    review_start_date DATE,
    review_end_date DATE,
    is_published INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
    CHECK (is_published IN (0, 1)),
    CHECK (review_end_date IS NULL OR review_end_date >= review_start_date)
);
```

### Peewee модель

```python
class StudentsReviews(Model):
    student_id = ForeignKeyField(Students, backref="students_reviews", on_delete="CASCADE")
    review_text = TextField()
    review_date = DateField(constraints=[SQL("DATE('now')")])
    review_start_date = DateField()
    review_end_date = DateField()
    is_published = BooleanField(default=False)
    created_at = DateTimeField(constraints=[SQL("CURRENT_TIMESTAMP")])
    updated_at = DateTimeField(constraints=[SQL("CURRENT_TIMESTAMP")])
```

### Проблемы

1. ❌ `review_text` должно быть `null=False` (NOT NULL в SQL)
2. ❌ `review_start_date` и `review_end_date` должны быть `null=True` (nullable в SQL)
3. ❌ Неправильные constraints для default значений
4. ❌ `is_published` как BooleanField не соответствует SQL INTEGER
5. ✅ ForeignKeyField корректен
6. ✅ Check constraints правильно определены

### Рекомендации

- Добавить null=False для review_text
- Добавить null=True для review_start_date и review_end_date
- Заменить BooleanField на IntegerField для is_published
- Исправить default значения

## Общие проблемы во всех моделях

1. ❌ Неправильное использование `constraints=[SQL("CURRENT_TIMESTAMP")]` вместо `default`
2. ❌ Использование BooleanField вместо IntegerField для полей типа is_active, is_published
3. ❌ Отсутствие null=False для обязательных текстовых полей
4. ❌ Некорректные default значения для дат

## Критические проблемы

1. База данных не включает поддержку внешних ключей (`foreign_keys=1` pragma)
2. Отсутствуют индексы, которые есть в SQL
3. Неправильная типизация boolean полей
4. Некорректные default значения

## Заключение

Модели требуют значительной доработки для полного соответствия SQL структуре. Основные проблемы связаны с типами данных, default значениями и отсутствием некоторых индексов.

---

## Окончательные выводы по трем проблемам

### 1. ✅ Constraints с CURRENT_TIMESTAMP - ИСПРАВЛЕНО

**Проблема**: Неправильное использование `constraints=[SQL("CURRENT_TIMESTAMP")]`

**Правильное решение** (нашел в Context7):

```python
# Вариант 1: Python уровень (рекомендуемый)
created_at = DateTimeField(default=datetime.datetime.now)

# Вариант 2: База данных уровень
created_at = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")])
```

### 2. ✅ BooleanField в SQLite - НЕ ПРОБЛЕМА

**Анализ документации**: BooleanField в PeeWee автоматически корректно работает с SQLite INTEGER 0/1.

**Вывод**: Использование BooleanField для is_active, is_published **КОРРЕКТНО** - не требует изменений.

### 3. ✅ Null=False по умолчанию - ПОДТВЕРЖДЕНО

**Документация**: В PeeWee все поля по умолчанию имеют `null=False` (NOT NULL).

**Рекомендация**: Явно указывать `null=False` для ясности кода в обязательных полях.

---

## Итоговые критические проблемы

### Основные проблемы во всех моделях

1. **❌ КРИТИЧНО**: Неправильные constraints для timestamp полей
   - Текущее: `constraints=[SQL("CURRENT_TIMESTAMP")]`
   - Нужно: `default=datetime.datetime.now` или `constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")]`

2. **❌ Конфигурация базы**: Отсутствует `foreign_keys=1` pragma для SQLite

   ```python
   db = SqliteDatabase('app.db', pragmas={'foreign_keys': 1})
   ```

3. **❌ Обязательные поля**: Отсутствует явное указание `null=False` для полей, помеченных NOT NULL в SQL

### Модели требующие исправления

- **Groups**: исправить created_at, добавить updated_at
- **Students**: исправить timestamp поля, добавить null=False
- **OnlineLessons**: исправить все default значения
- **StudentsOnlineLessons**: исправить timestamp поля
- **Homeworks**: исправить timestamp поля, добавить null=False
- **HomeworksStudents**: исправить timestamp поля
- **StudentsReviews**: исправить timestamp поля, добавить null=False

**Общий вывод**: Структура моделей в целом корректна, но требует исправления способа задания default значений и явного указания null=False для обязательных полей.
