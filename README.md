# Projekt Zespołowy Biznes Elektroniczny

Implementacja PrestaShop 1.7.8 przy użyciu Dockera, z własnym scrapperem, restapi importującym zescrapowane produkty, testami selenium.

## Wymagania

Prestashop
- Docker
- Docker Compose

Skrypty Scrappera
- requests
- beautifulsoup4

### Jak zainstalować Docker i Docker Compose

1.  **Zaktualizuj listę pakietów:**
    ```bash
    sudo apt update
    ```

2.  **Zainstaluj Docker i Docker Compose:**
    ```bash
    sudo apt install -y docker.io docker-compose
    ```

3.  **Napraw uprawnienia (pozwala na uruchamianie Dockera bez 'sudo'):**
    ```bash
    sudo usermod -aG docker $USER
    ```

4.  **WAŻNE:** Zrestartuj komputer, aby zastosować zmiany.

## Instalacja

1. **Sklonuj repozytorium**
    ```bash
    git clone https://github.com/mafinzyx/be_group_project.git
    cd ./be_group_project/prestashop
    ```

2. **Wygeneruj certyfikaty SSL**
    ```bash
    mkdir -p certs
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout certs/prestashop.key -out certs/prestashop.crt
    ```
    **WAŻNE:** Kiedy zapytany o "Common Name (CN): " wpisz: `localhost`. Pomiń pozostałe pola wciskając enter.

3. **Uruchom środowisko**
    ```bash
    docker-compose up -d
    ```
    To zazwyczaj trwa chwile, pierwsze uruchomienie trwa dłużej

    **Jeśli dostajesz błędy "Pythonowe"** spróbuj użyć:
    ```bash
    sudo apt install python3-setuptools
    ```
    a potem ponów użycie `docker-compose up -d`

    Następnie przydziel poprawne uprawnienia dostępu do projektu

    ```bash
    sudo chmod -R 777 .
    ```

    Jeśli kiedykolwiek będziesz musiał zresetować Dockera lub bazę danych, użyj:
    ```bash
    docker-compose down -v
    docker-compose up -d
    ```

4. **Dostęp do sklepu**\
    Po uruchomieniu środowiska udaj się na:\
    http://localhost:80 \
    Panel administracyjny strony:\
    http://localhost:80/admin191rnbbnl

5. **Zapisywanie zmian w bazie danych (Dodane produkty itp.)**
    Jeśli zmodyfikowałeś dane w bazie, musisz wykonać jej zrzut (dump), aby zapisać zmiany:
    ```bash
    sudo docker exec prestashop_db mysqldump -u root -pprestashop prestashop > dumps/init.sql
    ```

    Następnie wyślij zmiany na Gita:
    ```bash
    git add .
    git commit -m "Added X products and updated DB"
    git push
    ```

6. **Wczytywanie zmian w bazie od innych (Restartowanie Bazy Danych)**\
    Jeśli inny członek zespołu zmodyfikował bazę danych (`init.sql`), musisz przeładować wolumen:
    ```bash
    docker-compose down -v
    docker-compose up -d
    ```

7. **Praca ze scrapperem**\
    Aby skrypty działały poprawnie, należy zainstalować biblioteki w module venv:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```
8. **Testy**
   ```bash
    sudo apt update
    sudo apt install -y firefox firefox-geckodriver
    cd ~/be_group_project/tests/selenium
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install selenium
    python3 test_shop.py
   ```
## Dane logowania

**Panel Administratora Prestashop:**\
email: `prestashop@prestashop.com`
password: `prestashop`

**Baza Danych:**\
login: `prestashop`
password: `prestashop`

**Klucz API Webservice:**\
`R7FM7TCGA6NJRJU49MFTSJDP2JQ481U1`

Szczegóły konfiguracji znajdują się w pliku `docker-compose.yml`

## Authors

[![GitHub - Danylo Zherzdiev](https://img.shields.io/badge/GitHub-Danylo_Zherzdiev-181717?style=for-the-badge&logo=github)](https://github.com/mafinzyx)   [![GitHub - Danylo Lohachov](https://img.shields.io/badge/GitHub-Danylo_Lohachov-181717?style=for-the-badge&logo=github)](https://github.com/eternaki) [![GitHub - Maciej Blawat](https://img.shields.io/badge/GitHub-Maciej_Blawat-181717?style=for-the-badge&logo=github)](https://github.com/maciejblawat) [![GitHub - Maciej Blawat](https://img.shields.io/badge/GitHub-Mateusz_Grzonka-181717?style=for-the-badge&logo=github)]([https://github.com/maciejblawat](https://github.com/mateushhh)) [![GitHub - Maria Volkova](https://img.shields.io/badge/GitHub-Maria_Volkova-181717?style=for-the-badge&logo=github)](https://github.com/mvollkova)
