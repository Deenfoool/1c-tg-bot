import sqlite3
import re

# Путь к БД и файлу с данными
DB_NAME = 'catalog.db'
INPUT_FILE = 'differential.txt'

def connect_db():
    conn = sqlite3.connect(DB_NAME)
    return conn.cursor(), conn

def create_tables(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id INTEGER,
            name TEXT,
            description TEXT,
            image_url TEXT,
            FOREIGN KEY(model_id) REFERENCES models(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id INTEGER,
            number TEXT,
            name TEXT,
            quantity INTEGER,
            FOREIGN KEY(node_id) REFERENCES nodes(id)
        )
    ''')

def insert_model(cursor, model_name):
    cursor.execute("SELECT id FROM models WHERE name = ?", (model_name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    cursor.execute("INSERT INTO models (name) VALUES (?)", (model_name,))
    return cursor.lastrowid

def insert_node(cursor, model_id, node_name, image_url, description=""):
    cursor.execute('''
        INSERT INTO nodes (model_id, name, description, image_url)
        VALUES (?, ?, ?, ?)
    ''', (model_id, node_name, description, image_url))
    return cursor.lastrowid

def process_line(line):
    line = line.strip()
    if not line:
        return None
    # Найдем номер детали, количество и название
    match = re.match(r'([^\t]+)\t(\d+)\s*', line)
    if not match:
        return None
    number, quantity = match.groups()
    quantity = int(quantity)
    return number, quantity

def main():
    cursor, conn = connect_db()
    create_tables(cursor)

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        lines = [line.rstrip('\n') for line in f]

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Определение названия узла
        if re.match(r'.*\. Каталог \d+г\.$', line):
            node_title = line.split('.')[0].strip()
            model_name = "мтз-80"  # можно определить по контексту
            model_id = insert_model(cursor, model_name)
            i += 1
            if i >= len(lines):
                break
            image_url = lines[i].strip()
            node_id = insert_node(cursor, model_id, node_title, image_url=image_url)
            print(f"Добавлен узел: {node_title} для модели {model_name}")
            i += 1
            continue

        # Обработка деталей
        processed = process_line(line)
        if processed:
            number, quantity = processed
            i += 1
            next_line = lines[i].strip() if i < len(lines) else ''
            name = next_line or 'Не указано'
            cursor.execute('''
                INSERT INTO parts (node_id, number, name, quantity)
                VALUES (?, ?, ?, ?)
            ''', (node_id, number, name, quantity))
            print(f"Добавлена деталь: {number} - {name}, кол-во: {quantity}")

        i += 1

    conn.commit()
    conn.close()
    print("Импорт завершен.")

if __name__ == '__main__':
    main()
