#!/bin/bash

# WhatsMyFinder Launcher
# Version: 2.0.0
# Author: @Osinter_Telegram

echo "================================================"
echo "🔍 WhatsMyFinder - OSINT Username Search Tool"
echo "================================================"
echo "Version: 2.0.0"
echo "Author: @Osinter_Telegram"
echo "Database: WebBreacher/WhatsMyName"
echo "================================================"

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не установлен"
    echo "Установите Python3:"
    echo "  Ubuntu/Debian: sudo apt install python3"
    echo "  Termux: pkg install python"
    echo "  Fedora: sudo dnf install python3"
    exit 1
fi

# Проверка зависимостей
echo "📦 Проверка зависимостей..."
if ! python3 -c "import aiohttp" &> /dev/null; then
    echo "Установка зависимостей..."
    pip install -r requirements.txt
fi

# Проверка базы данных
if [ ! -f "wmn-data.json" ]; then
    echo "⚠️  База данных не найдена"
    echo "Скачать базу данных:"
    echo "  wget https://raw.githubusercontent.com/WebBreacher/WhatsMyName/main/wmn-data.json"
    echo "Или поместите wmn-data.json в текущую директорию"
    read -p "Продолжить без базы данных? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Создание папок
mkdir -p reports/html reports/csv

# Запуск приложения
echo "🚀 Запуск WhatsMyFinder..."
python3 whatsmyfinder.py

echo "================================================"
echo "✅ WhatsMyFinder завершил работу"
echo "📁 Отчеты сохранены в папке reports/"
echo "================================================"