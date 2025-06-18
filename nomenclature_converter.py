import os
import json

# Путь к исходному .txt файлу
input_file = 'nomenclature1.txt'

# Путь к выходному JSON файлу
output_file = 'nomenclature.json'

# Чтение данных из файла
with open(input_file, 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f if line.strip()]

# Обработка строк
nomenclature = []
for line in lines:
    # Разделение по первому пробелу
    parts = line.split(' ', 1)
    if len(parts) < 2:
        continue  # пропустить строки без пробела

    code = parts[0]
    name = parts[1]

    # Проверка: code должен содержать только цифры
    if code.isdigit():
        nomenclature.append({'code': code, 'name': name})
    else:
        print(f"Пропущена строка с некорректным кодом: {line}")

# Сохранение результата в JSON
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(nomenclature, f, ensure_ascii=False, indent=4)

print(f"Обработано {len(nomenclature)} записей. Результат сохранён в '{output_file}'.")