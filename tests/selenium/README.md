# Testy Automatyczne Selenium dla PrestaShop

Skrypt wykonujący testy automatyczne dla sklepu PrestaShop zgodnie z wymaganiami projektu.

## Wymagania

- Python 3.6+
- Firefox lub Chrome (lub odpowiedni driver zostanie pobrany automatycznie)
- Dostęp do sklepu PrestaShop (lokalnie lub w klastrze)

## Instalacja

### 1. Instalacja przeglądarki (Linux)

**Firefox:**
```bash
sudo apt update
sudo apt install -y firefox firefox-geckodriver
```

**Chrome:**
```bash
# Pobierz i zainstaluj Chrome z oficjalnej strony
# lub użyj:
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
```

### 2. Przygotowanie środowiska

```bash
cd tests/selenium
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Uruchomienie testów

### Lokalne środowisko (Docker Compose)

```bash
# Użyj skryptu uruchamiającego (domyślnie Firefox)
./run_tests.sh

# Lub bezpośrednio
python3 test_shop.py

# Z wyborem przeglądarki
python3 test_shop.py http://localhost:80 chrome
python3 test_shop.py http://localhost:80 firefox
python3 test_shop.py http://localhost:80 both  # Oba przeglądarki
```

### Sklep wdrożony w klastrze

```bash
# Ustaw URL sklepu jako zmienną środowiskową
export SHOP_URL="http://twoj-sklep.example.com"
./run_tests.sh

# Lub przekaż URL jako argument
./run_tests.sh http://twoj-sklep.example.com

# Wybór przeglądarki
export BROWSER="chrome"  # lub "firefox" lub "both"
./run_tests.sh http://twoj-sklep.example.com

# Lub bezpośrednio w Pythonie
python3 test_shop.py http://twoj-sklep.example.com chrome
```

### Wybór przeglądarki

```bash
# Firefox (domyślna)
export BROWSER="firefox"
./run_tests.sh

# Chrome
export BROWSER="chrome"
./run_tests.sh

# Oba przeglądarki (testy uruchomią się dwukrotnie)
export BROWSER="both"
./run_tests.sh
```

### Tryb headless (bez interfejsu graficznego)

```bash
export HEADLESS=true
export BROWSER="chrome"  # lub "firefox"
./run_tests.sh http://twoj-sklep.example.com
```

### Własne dane logowania

```bash
export TEST_EMAIL="twoj@email.com"
export TEST_PASSWORD="twoje-haslo"
./run_tests.sh
```

## Scenariusz testowy

Skrypt wykonuje następujące testy (czas wykonania < 5 min):

1. **Dodanie 10 produktów do koszyka** (różne kategorie)
2. **Wyszukanie produktu po nazwie** → dodanie losowego wyniku do koszyka
3. **Usunięcie 3 produktów z koszyka**
4. **Rejestracja nowego konta**
5. **Checkout (zamówienie)**
6. **Płatność: Przy odbiorze**
7. **Wybór jednego z przewoźników**
8. **Zatwierdzenie zamówienia**
9. **Sprawdzenie statusu zamówienia**
10. **Pobranie faktury VAT**

## Konfiguracja dla klastra

Aby testy działały prawidłowo na sklepie wdrożonym w klastrze:

1. **Ustaw zmienną środowiskową SHOP_URL** na adres sklepu w klastrze:
   ```bash
   export SHOP_URL="https://twoj-sklep-w-klastrze.com"
   ```

2. **Upewnij się, że sklep jest dostępny** z maszyny, na której uruchamiasz testy:
   ```bash
   curl -I https://twoj-sklep-w-klastrze.com
   ```

3. **Jeśli sklep wymaga uwierzytelnienia**, ustaw odpowiednie zmienne:
   ```bash
   export TEST_EMAIL="twoj@email.com"
   export TEST_PASSWORD="twoje-haslo"
   ```

4. **Uruchom testy**:
   ```bash
   ./run_tests.sh
   ```

## Rozwiązywanie problemów

### Firefox nie jest zainstalowany
```bash
sudo apt install -y firefox firefox-geckodriver
```

### Chrome nie jest zainstalowany
```bash
# Linux
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb

# macOS (użyj Homebrew)
brew install --cask google-chrome
```

### Wybór przeglądarki
Jeśli masz problemy z jedną przeglądarką, spróbuj drugiej:
```bash
export BROWSER="chrome"  # Zamiast Firefox
./run_tests.sh
```

### Błędy połączenia z sklepem
- Sprawdź czy URL jest poprawny
- Sprawdź czy sklep jest dostępny: `curl -I <URL>`
- Sprawdź czy nie ma problemów z siecią/firewallem

### Błędy podczas testów
- Sprawdź logi w konsoli
- Upewnij się, że sklep ma produkty w bazie danych
- Sprawdź czy wszystkie wymagane moduły PrestaShop są aktywne

## Struktura plików

```
tests/selenium/
├── test_shop.py          # Główny skrypt testowy
├── run_tests.sh          # Skrypt uruchamiający testy
├── requirements.txt      # Zależności Python
└── README.md             # Ta dokumentacja
```

## Autorzy

Projekt zespołowy Biznes Elektroniczny
