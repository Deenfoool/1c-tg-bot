@echo off
setlocal

:: Путь к интерпретатору Python (если не в PATH, укажите полный путь)
set PYTHON=python

:: Имя входного файла
set INPUT_FILE=nomenclature.txt

:: Имя выходного файла
set OUTPUT_FILE=nomenclature.json

:: Проверяем наличие входного файла
if not exist "%INPUT_FILE%" (
    echo ❌ Файл "%INPUT_FILE%" не найден.
    pause
    exit /b 1
)

:: Запуск скрипта
echo 🔁 Начало конвертации...
"%PYTHON%" convert_txt_to_json.py "%INPUT_FILE%" "%OUTPUT_FILE%"

:: Проверяем результат
if exist "%OUTPUT_FILE%" (
    echo ✅ Данные успешно сохранены в "%OUTPUT_FILE%"
) else (
    echo ❌ Не удалось создать файл "%OUTPUT_FILE%"
)

pause