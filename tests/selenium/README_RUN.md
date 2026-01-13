# Selenium Tests - Инструкция по запуску

## Быстрый запуск

Из **корневой директории проекта** выполните:

```bash
./run_selenium_tests.sh
```

Скрипт автоматически:
- ✅ Проверит доступность магазина
- ✅ Создаст виртуальное окружение (если нужно)
- ✅ Установит зависимости
- ✅ Проверит наличие Firefox и geckodriver
- ✅ Запустит все тесты

## Что делает тест

Тест выполняет следующие сценарии:

1. **Добавление 10 продуктов** - 5 из категории "wina" + 5 из "delikatesy"
2. **Поиск и добавление** - случайный продукт по поисковому запросу "Wino"
3. **Удаление 3 продуктов** из корзины
4. **Регистрация** нового клиента
5. **Оформление заказа**:
   - Ввод адреса доставки
   - Выбор второго перевозчика (если доступен)
   - Выбор способа оплаты
   - Подтверждение заказа
6. **Проверка статуса** заказа
7. **Попытка скачать** фактуру (если доступна)

## Требования

### Обязательно:
- 🦊 **Firefox** - установлен и доступен
- 🔧 **geckodriver** - установлен и в PATH
- 🐳 **PrestaShop** - магазин запущен на `http://127.0.0.1`

### Установка зависимостей (если нужно):

```bash
# Установка Firefox
brew install --cask firefox

# Установка geckodriver
brew install geckodriver

# Установка Python пакетов
pip install -r requirements.txt
```

## Запуск из директории тестов

Если хотите запустить напрямую из `tests/selenium/`:

```bash
cd tests/selenium
source venv/bin/activate
python test_shop.py
```

## Примечания

- Тест создаёт **нового пользователя** при каждом запуске
- Email генерируется случайно: `student[число]@mail.pl`
- Окно браузера **видимое** - можно наблюдать за выполнением
- Тест занимает **~2-3 минуты**

## Структура тестов

```
tests/selenium/
├── test_shop.py              # Основной файл с тестами
├── requirements.txt          # Python зависимости
├── venv/                     # Виртуальное окружение
├── INSTRUKCJA_TESTOWANIA.md  # Детальная инструкция (PL)
└── README_RUN.md            # Эта инструкция
```

## Troubleshooting

### Магазин недоступен
```bash
# Запустите Docker контейнеры
docker-compose up -d

# Проверьте статус
docker-compose ps
```

### Firefox не найден
```bash
# macOS
brew install --cask firefox

# Linux
sudo apt install firefox
```

### geckodriver не найден
```bash
# macOS
brew install geckodriver

# Linux
wget https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-linux64.tar.gz
tar -xvzf geckodriver-v0.36.0-linux64.tar.gz
sudo mv geckodriver /usr/local/bin/
```

## Результат успешного выполнения

```
KROK: Dodawanie 5 produktów z: http://127.0.0.1/en/3-wina
-> Pomyślnie dodano 5 produktów.
KROK: Dodawanie 5 produktów z: http://127.0.0.1/en/100-delikatesy
-> Pomyślnie dodano 5 produktów.
KROK: Wyszukiwanie frazy 'Wino' i wybór losowego produktu...
-> Produkt z wyszukiwania dodany.
KROK: Usuwanie 3 produktów z koszyka...
-> Usunięto produkt nr 3
KROK: Rejestracja nowego klienta...
-> Rejestracja zakończona sukcesem
KROK: Realizacja zamówienia (Checkout)...
-> Zamówienie złożone! Numer: XXXXX
KROK: Sprawdzanie statusu i faktury...
-> Status zamówienia: Awaiting check payment
Test zakończony.
```
