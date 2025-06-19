from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import json
import sqlite3
import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

NOMENCLATURE_FILE = '../nomenclature.json'
DB_NAME = '../catalog.db'

def load_nomenclature():
    try:
        with open(NOMENCLATURE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as e:
        print(f"Ошибка чтения JSON-файла: {e}")
        return []

def save_nomenclature(nomenclature):
    try:
        with open(NOMENCLATURE_FILE, 'w', encoding='utf-8') as f:
            json.dump(nomenclature, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Ошибка сохранения файла: {e}")

@app.route('/')
def index():
    items = load_nomenclature()
    return render_template('index.html', items=items)

@app.route('/add', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        code = request.form.get('code')
        name = request.form.get('name')
        if not code or not name:
            return "Неверные данные", 400
        if not code.isdigit() or len(code) < 5:
            return "Код должен быть не меньше 5 цифр", 400
        nomenclature = load_nomenclature()
        if any(item['code'] == code for item in nomenclature):
            return "Элемент с таким кодом уже существует", 400
        nomenclature.append({'code': code, 'name': name})
        save_nomenclature(nomenclature)
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    items = load_nomenclature()
    results = [item for item in items if query.lower() in item['name'].lower() or query == item['code']]
    return render_template('index.html', items=results)

@app.route('/delete/<code>')
def delete_item(code):
    nomenclature = load_nomenclature()
    new_nomenclature = [item for item in nomenclature if item['code'] != code]
    if len(nomenclature) == len(new_nomenclature):
        return "Запись не найдена", 404
    save_nomenclature(new_nomenclature)
    return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if not file or not file.filename.endswith('.txt'):
        return "Формат файла должен быть .txt", 400
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
        nomenclature = []
        for line in lines:
            parts = line.split(' ', 1)
            if len(parts) < 2:
                continue
            code, name = parts[0], parts[1]
            if code.isdigit():
                nomenclature.append({'code': code, 'name': name})
        save_nomenclature(nomenclature)
        os.remove(file_path)
        return redirect(url_for('index'))
    except Exception as e:
        return f"Ошибка обработки файла: {str(e)}", 500

@app.route('/db')
def db_browser():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    models_sql = "SELECT * FROM models;"
    nodes_sql = "SELECT * FROM nodes;"
    parts_sql = "SELECT * FROM parts;"

    models = cursor.execute(models_sql).fetchall()
    nodes = cursor.execute(nodes_sql).fetchall()
    parts = cursor.execute(parts_sql).fetchall()

    conn.close()
    return render_template('db.html', models=models, nodes=nodes, parts=parts)

if __name__ == '__main__':
    app.run(debug=True)
