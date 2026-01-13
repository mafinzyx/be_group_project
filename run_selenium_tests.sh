#!/bin/bash

# Скрипт для запуска Selenium тестов PrestaShop
# Использование: ./run_selenium_tests.sh

set -e

echo "=================================="
echo "🧪 Selenium Tests - PrestaShop"
echo "=================================="
echo ""

# Проверка доступности магазина
SHOP_URL="http://localhost:8080"
echo "🔍 Проверка доступности магазина: ${SHOP_URL}"
if curl -s --head --fail "${SHOP_URL}" > /dev/null; then
    echo "✅ Магазин доступен"
else
    echo "❌ ОШИБКА: Магазин недоступен на ${SHOP_URL}"
    echo "   Убедитесь что Docker контейнеры запущены: docker-compose up -d"
    exit 1
fi
echo ""

# Переход в директорию с тестами
TEST_DIR="tests/selenium"
echo "📁 Переход в директорию: ${TEST_DIR}"
cd "${TEST_DIR}" || exit 1
echo ""

# Проверка наличия виртуального окружения
if [ ! -d "venv" ]; then
    echo "📦 Создание виртуального окружения..."
    python3 -m venv venv
    echo "✅ Виртуальное окружение создано"
    echo ""
fi

# Активация виртуального окружения
echo "🔧 Активация виртуального окружения..."
source venv/bin/activate
echo ""

# Установка зависимостей
echo "📥 Установка зависимостей..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo "✅ Зависимости установлены"
echo ""

# Проверка Firefox и geckodriver
echo "🦊 Проверка Firefox и geckodriver..."
if ! command -v firefox &> /dev/null; then
    echo "❌ ОШИБКА: Firefox не установлен"
    echo "   Установите Firefox: brew install --cask firefox"
    exit 1
fi
if ! command -v geckodriver &> /dev/null; then
    echo "❌ ОШИБКА: geckodriver не установлен"
    echo "   Установите geckodriver: brew install geckodriver"
    exit 1
fi
echo "✅ Firefox и geckodriver установлены"
echo ""

# Запуск тестов
echo "=================================="
echo "🚀 Запуск тестов..."
echo "=================================="
echo ""

python test_shop.py

# Возврат к корневой директории
cd ../..

echo ""
echo "=================================="
echo "✅ Тесты завершены!"
echo "=================================="
