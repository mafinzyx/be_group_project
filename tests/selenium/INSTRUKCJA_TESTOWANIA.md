# Instrukcja Testowania - Krok po Kroku

## 📋 Wymagania wstępne

Przed uruchomieniem testów upewnij się, że masz:
- ✅ Docker i Docker Compose zainstalowane
- ✅ Python 3.6+ zainstalowany
- ✅ Firefox lub Chrome zainstalowany (lub odpowiedni driver zostanie pobrany automatycznie)

## 🚀 Krok 1: Uruchomienie sklepu PrestaShop

**TAK, musisz uruchomić aplikację przed testowaniem!**

### 1.1. Przejdź do katalogu PrestaShop

```bash
cd be_group_project/prestashop
```

### 1.2. Sprawdź czy kontenery są uruchomione

```bash
docker-compose ps
# lub
docker compose ps
```

Jeśli kontenery nie są uruchomione, zobaczysz pustą listę lub błąd.

### 1.3. Uruchom sklep (jeśli nie jest uruchomiony)

```bash
# Uruchom kontenery w tle
docker-compose up -d
# lub (nowsza wersja Docker)
docker compose up -d
```

**Pierwsze uruchomienie może zająć kilka minut** - Docker pobierze obrazy i skonfiguruje środowisko.

### 1.4. Sprawdź czy sklep działa

Otwórz w przeglądarce:
- **Sklep:** http://localhost:80
- **Panel admina:** http://localhost:80/admin191rnbbnl

Jeśli widzisz stronę sklepu - wszystko działa! ✅

### 1.5. Sprawdź status kontenerów

```bash
docker-compose ps
```

Powinieneś zobaczyć coś takiego:
```
NAME                STATUS          PORTS
prestashop_db       Up              ...
prestashop_web      Up              0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
```

## 🧪 Krok 2: Przygotowanie środowiska testowego

### 2.1. Przejdź do katalogu z testami

```bash
cd ../../tests/selenium
```

### 2.2. Sprawdź czy masz przeglądarkę

**Firefox:**
```bash
firefox --version
```

Jeśli nie masz Firefox (Linux):
```bash
sudo apt update
sudo apt install -y firefox firefox-geckodriver
```

**Chrome:**
```bash
google-chrome --version
# lub na macOS:
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version
```

Na macOS Firefox i Chrome zwykle są już zainstalowane.

### 2.3. Utwórz i aktywuj środowisko wirtualne Python

```bash
python3 -m venv venv
source venv/bin/activate  # Na macOS/Linux
# Na Windows: venv\Scripts\activate
```

Po aktywacji zobaczysz `(venv)` na początku linii w terminalu.

### 2.4. Zainstaluj zależności

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 🎯 Krok 3: Uruchomienie testów

### Opcja A: Użyj skryptu uruchamiającego (ZALECANE)

```bash
# Upewnij się, że jesteś w katalogu tests/selenium
cd tests/selenium

# Uruchom skrypt (domyślnie Firefox)
./run_tests.sh

# Lub z wyborem przeglądarki
export BROWSER="chrome"
./run_tests.sh

# Lub testuj oba przeglądarki
export BROWSER="both"
./run_tests.sh
```

Skrypt automatycznie:
- ✅ Sprawdzi dostępność sklepu
- ✅ Utworzy środowisko wirtualne (jeśli nie istnieje)
- ✅ Zainstaluje zależności
- ✅ Uruchomi wszystkie testy
- ✅ Wyświetli podsumowanie

### Opcja B: Ręczne uruchomienie

```bash
# Aktywuj środowisko wirtualne
source venv/bin/activate

# Uruchom testy bezpośrednio (Firefox - domyślnie)
python3 test_shop.py

# Lub z wyborem przeglądarki
python3 test_shop.py http://localhost:80 chrome
python3 test_shop.py http://localhost:80 firefox
python3 test_shop.py http://localhost:80 both  # Oba przeglądarki
```

### Opcja C: Testowanie sklepu w klastrze

Jeśli masz sklep wdrożony w klastrze (nie lokalnie):

```bash
# Ustaw URL sklepu
export SHOP_URL="http://twoj-sklep-w-klastrze.com"

# Wybierz przeglądarkę (opcjonalnie)
export BROWSER="chrome"  # lub "firefox" lub "both"

# Uruchom testy
./run_tests.sh
```

## 📊 Krok 4: Co powinieneś zobaczyć

### 4.1. Podczas uruchamiania

Zobaczysz coś takiego:

```
=== Skrypt testów automatycznych PrestaShop ===

Sprawdzanie dostępności sklepu: http://localhost:80
✓ Sklep jest dostępny

Tworzenie środowiska wirtualnego...
Aktywacja środowiska wirtualnego...
Aktualizacja pip...
Instalacja zależności...

=== Uruchamianie testów ===
URL sklepu: http://localhost:80
Tryb headless: false
Email testowy: prestashop@prestashop.com

============================================================
Rozpoczynanie testów automatycznych dla: http://localhost:80
============================================================

✓ Przeglądarka uruchomiona pomyślnie

=== Test 1: Dodawanie 10 produktów do koszyka ===
  Dodano produkt 1/10
  Dodano produkt 2/10
  ...
✓ Dodanie 10 produktów: Dodano 10 produktów

=== Test 2: Wyszukanie i dodanie produktu ===
✓ Wyszukanie i dodanie produktu: Znaleziono i dodano produkt z wyszukiwania 'wino'

... (i tak dalej dla wszystkich testów) ...

============================================================
PODSUMOWANIE TESTÓW
============================================================
✓ Dodanie 10 produktów: Dodano 10 produktów
✓ Wyszukanie i dodanie produktu: Znaleziono i dodano produkt z wyszukiwania 'wino'
✓ Usunięcie 3 produktów: Usunięto 3 produktów
✓ Rejestracja: Utworzono konto: test_abc123@example.com
✓ Wybór przewoźnika: Wybrano przewoźnika
✓ Wybór płatności: Wybrano płatność przy odbiorze
✓ Zatwierdzenie zamówienia: Zamówienie złożone
✓ Sprawdzenie statusu zamówienia: Status: Oczekiwanie na płatność
✓ Pobranie faktury VAT: Znaleziono link do faktury: ...

Wynik: 10/10 testów zakończonych pomyślnie
============================================================

✓ Wszystkie testy zakończone pomyślnie
```

### 4.2. Otworzy się przeglądarka

Podczas testów zobaczysz, jak przeglądarka (Firefox lub Chrome):
- Otwiera stronę sklepu
- Dodaje produkty do koszyka
- Wypełnia formularze
- Wykonuje zamówienie

**To normalne!** Testy używają prawdziwej przeglądarki.

Jeśli wybrałeś `BROWSER="both"`, testy uruchomią się dwukrotnie - raz w Firefox, raz w Chrome.

### 4.3. Wynik końcowy

**Sukces:** Wszystkie testy zakończone pomyślnie ✅
```
Wynik: 10/10 testów zakończonych pomyślnie
```

**Częściowy sukces:** Niektóre testy nie powiodły się ⚠️
```
Wynik: 8/10 testów zakończonych pomyślnie
✗ Rejestracja: Błąd: Email już istnieje
✗ Zatwierdzenie zamówienia: Błąd: Nie znaleziono przycisku
```

## ⚠️ Rozwiązywanie problemów

### Problem: "Nie można połączyć się z http://localhost:80"

**Rozwiązanie:**
1. Sprawdź czy kontenery są uruchomione:
   ```bash
   docker-compose ps
   ```
2. Jeśli nie, uruchom je:
   ```bash
   docker-compose up -d
   ```
3. Poczekaj 30-60 sekund i sprawdź ponownie:
   ```bash
   curl -I http://localhost:80
   ```

### Problem: "Firefox nie jest zainstalowany"

**Rozwiązanie (Linux):**
```bash
sudo apt update
sudo apt install -y firefox firefox-geckodriver
```

**Rozwiązanie (macOS):**
Firefox powinien być już zainstalowany. Jeśli nie:
```bash
brew install --cask firefox
```

**Alternatywa - użyj Chrome:**
```bash
export BROWSER="chrome"
./run_tests.sh
```

### Problem: "Chrome nie jest zainstalowany"

**Rozwiązanie (Linux):**
```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
```

**Rozwiązanie (macOS):**
```bash
brew install --cask google-chrome
```

**Alternatywa - użyj Firefox:**
```bash
export BROWSER="firefox"
./run_tests.sh
```

### Problem: "Nie znaleziono produktów" lub "Koszyk jest pusty"

**Rozwiązanie:**
1. Upewnij się, że w sklepie są produkty
2. Sprawdź czy produkty są widoczne na stronie głównej
3. Możesz zaimportować produkty używając skryptów z katalogu `scrapper/`

### Problem: "Błąd podczas rejestracji: Email już istnieje"

**Rozwiązanie:**
To normalne - test generuje losowy email, ale może się zdarzyć kolizja. Testy powinny działać mimo tego błędu.

### Problem: Testy są zbyt wolne

**Rozwiązanie:**
Możesz uruchomić testy w trybie headless (bez interfejsu graficznego):
```bash
export HEADLESS=true
export BROWSER="chrome"  # Chrome zwykle jest szybszy w headless
./run_tests.sh
```

### Problem: Chcesz przetestować w obu przeglądarkach

**Rozwiązanie:**
Uruchom testy w obu przeglądarkach jednocześnie:
```bash
export BROWSER="both"
./run_tests.sh
```

Testy uruchomią się najpierw w Firefox, potem w Chrome. Zobaczysz osobne podsumowania dla każdej przeglądarki.

## 📝 Sprawdzenie wyników

Po zakończeniu testów:

1. **Sprawdź podsumowanie** - na końcu zobaczysz listę wszystkich testów z wynikami
2. **Sprawdź kod wyjścia:**
   ```bash
   echo $?  # Powinno zwrócić 0 jeśli wszystkie testy przeszły
   ```
3. **Sprawdź logi** - wszystkie komunikaty są wyświetlane w konsoli

## 🎉 Gotowe!

Jeśli widzisz "Wszystkie testy zakończone pomyślnie" - gratulacje! ✅

Skrypt działa prawidłowo i jest gotowy do użycia na sklepie wdrożonym w klastrze.
