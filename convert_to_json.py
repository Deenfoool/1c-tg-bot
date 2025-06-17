import json

# Имя входного текстового файла
INPUT_FILE = 'nomenclature.txt'
# Имя выходного JSON-файла
OUTPUT_FILE = 'nomenclature.json'

def parse_line(line):
    # Разделяем строку по пробелам (первый элемент - код)
    parts = line.strip().split()
    if len(parts) < 3:
        return None  # Пропускаем строки, которые не соответствуют формату

    code = parts[0]
    name = ' '.join(parts[1:-1])  # Все кроме первого и последнего элемента — наименование
    article = parts[-1]  # Последний элемент — артикул

    return {
        "code": code,
        "name": name,
        "article": article
    }

def convert_txt_to_json(input_file, output_file):
    nomenclature = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            item = parse_line(line)
            if item:
                nomenclature.append(item)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(nomenclature, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    convert_txt_to_json(INPUT_FILE, OUTPUT_FILE)
    print(f"Данные успешно сохранены в {OUTPUT_FILE}")
