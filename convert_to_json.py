import re
import json

def parse_line(line):
    # Регулярное выражение для извлечения кода, наименования и артикула
    match = re.match(r'$$(\d+)$$ (.*) $([^$$]*)$', line)
    if not match:
        return None
    
    code = match.group(1)
    full_name_part = match.group(2).strip()
    article = match.group(3).strip()

    # Извлекаем наименование (до первой скобки или до слова в скобках)
    name_match = re.match(r'(.*?) $$', full_name_part)
    if name_match:
        name = name_match.group(1).strip()
    else:
        name = full_name_part.strip()

    return {
        code: {
            "наименование": name,
            "артикул": article
        }
    }

# Чтение данных из текстового файла
input_file = 'nomen.txt'
output_file = 'nomenclature.json'

data = {}

with open(input_file, 'r', encoding='utf-8') as f:
    for line in f:
        parsed = parse_line(line)
        if parsed:
            data.update(parsed)

# Сохранение результата в JSON
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print(f"✅ JSON-файл '{output_file}' успешно создан!")
