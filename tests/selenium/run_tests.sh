#!/bin/bash
# Skrypt uruchamiający testy automatyczne dla sklepu PrestaShop
# Obsługuje konfigurację dla środowiska lokalnego i klastra

set -e  # Zatrzymaj wykonanie przy błędzie

# Kolory dla wyjścia
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Skrypt testów automatycznych PrestaShop ===${NC}\n"

# Sprawdzenie czy Python3 jest zainstalowany
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python3 nie jest zainstalowany${NC}"
    exit 1
fi

# Pobranie URL sklepu z zmiennej środowiskowej lub argumentu
SHOP_URL="${SHOP_URL:-${1:-http://localhost:80}}"

# Sprawdzenie czy URL jest dostępny
echo -e "${YELLOW}Sprawdzanie dostępności sklepu: ${SHOP_URL}${NC}"
if ! curl -s --head --fail "${SHOP_URL}" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠ Ostrzeżenie: Nie można połączyć się z ${SHOP_URL}${NC}"
    echo -e "${YELLOW}  Testy będą kontynuowane, ale mogą się nie powieść.${NC}\n"
else
    echo -e "${GREEN}✓ Sklep jest dostępny${NC}\n"
fi

# Przejście do katalogu ze skryptami
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Sprawdzenie czy istnieje środowisko wirtualne
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Tworzenie środowiska wirtualnego...${NC}"
    python3 -m venv venv
fi

# Aktywacja środowiska wirtualnego
echo -e "${YELLOW}Aktywacja środowiska wirtualnego...${NC}"
source venv/bin/activate

# Aktualizacja pip
echo -e "${YELLOW}Aktualizacja pip...${NC}"
pip install --upgrade pip --quiet

# Instalacja zależności
echo -e "${YELLOW}Instalacja zależności...${NC}"
pip install -r requirements.txt --quiet

# Sprawdzenie dostępności przeglądarek
if [ "${BROWSER}" = "firefox" ] || [ "${BROWSER}" = "both" ]; then
    if ! command -v firefox &> /dev/null; then
        echo -e "${YELLOW}⚠ Firefox nie jest zainstalowany. Geckodriver zostanie pobrany automatycznie.${NC}"
    fi
fi

if [ "${BROWSER}" = "chrome" ] || [ "${BROWSER}" = "both" ]; then
    if ! command -v google-chrome &> /dev/null && ! command -v chromium &> /dev/null && ! command -v "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" &> /dev/null; then
        echo -e "${YELLOW}⚠ Chrome nie jest zainstalowany. Chromedriver zostanie pobrany automatycznie.${NC}"
    fi
fi

# Ustawienie zmiennej środowiskowej dla URL sklepu
export SHOP_URL="${SHOP_URL}"

# Opcjonalne zmienne środowiskowe
export HEADLESS="${HEADLESS:-false}"
export BROWSER="${BROWSER:-firefox}"  # firefox, chrome, lub both
export TEST_EMAIL="${TEST_EMAIL:-prestashop@prestashop.com}"
export TEST_PASSWORD="${TEST_PASSWORD:-prestashop}"

echo -e "\n${GREEN}=== Uruchamianie testów ===${NC}"
echo -e "URL sklepu: ${SHOP_URL}"
echo -e "Przeglądarka: ${BROWSER}"
echo -e "Tryb headless: ${HEADLESS}"
echo -e "Email testowy: ${TEST_EMAIL}\n"

# Uruchomienie testów
python3 test_shop.py "${SHOP_URL}" "${BROWSER}"

# Zapisanie kodu wyjścia
TEST_EXIT_CODE=$?

# Deaktywacja środowiska wirtualnego
deactivate

# Zwrócenie kodu wyjścia
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "\n${GREEN}✓ Wszystkie testy zakończone pomyślnie${NC}"
    exit 0
else
    echo -e "\n${RED}✗ Niektóre testy zakończyły się niepowodzeniem${NC}"
    exit $TEST_EXIT_CODE
fi
