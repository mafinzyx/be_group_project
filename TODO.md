1. Repozytorium i Organizacja Pracy (5 pkt)
    [X] Utworzenie repozytorium na GitHub/GitLab.
    [X] Dodanie członków zespołu do projektu.
    [X] Utworzenie struktury katalogów:
        /prestashop
        /prestashop/dumps
        /tests
        /scrapper
        /scrapper/data
    [X] Stworzenie pliku .gitignore (wykluczenie cache itp)
    [X] Stworzenie README.md (opis projektu, wersja softu, instrukcja uruchomienia, skład zespołu).
    [X] Organizacja pracy (Issues): Zadania opisane jako Issues i przypisane do osób.
    [X] Workflow Git: Praca na branchach roboczych -> Pull Request (PR/MR) -> Code Review -> Merge do main.

2. Scraping (5 pkt)
    [X] Napisanie skryptu scrapującego.
    [X] Pobranie danych: Kategorie, Podkategorie, Produkty (Nazwa, Opis, Cena, Atrybuty).
    [X] Pobranie zdjęć: Minimum 2 zdjęcia wysokiej rozdzielczości na produkt (nie miniatury!).
    [X] Zapis wyników: Plik wynikowy w kodowaniu UTF-8 w folderze repozytorium.

3. Środowisko i Instalacja PrestaShop (5 pkt)
    [X] Konfiguracja środowiska: Docker/docker-compose LUB maszyna wirtualna (Ubuntu).
    [X] Instalacja PrestaShop: Wersja 1.7.8.
    [ ] Certyfikat SSL: Wygenerowanie i wdrożenie certyfikatu (self-signed) -> wymuszenie HTTPS.
    [X] Czyszczenie: Usunięcie domyślnych produktów/kategorii/banerów z instalatora.

4. Import Danych (REST API) (5 pkt)
    [X] Napisanie skryptu importującego w Python/PHP łączącego się z API PrestaShop.
    [X] Import Kategorii i Podkategorii
    [X] Import Produktów
    [X] Zarządzanie stanami magazynowymi:
        Max 10 szt. każdego produktu.
        Część produktów ustawiona jako niedostępna.

5. Konfiguracja Sklepu (Backend) (Część z 5 pkt + 3 pkt)
    [X] Język: Interfejs użytkownika ustawiony na polski.
    [X] Płatności: Skonfigurowanie metod polskich (np. Przelew, Za pobraniem) - bez zewnętrznych integracji typu PayU. Usunięcie metod zagranicznych.
    [X] E-maile: Konfiguracja wysyłki powiadomień (rejestracja, zakup).
    [X] Przewoźnicy (Dostawa):
        Zdefiniowanie 2 nowych przewoźników.
        Różne opłaty dla przewoźników.
        Logika 1: Darmowa dostawa powyżej 2000 zł.
        Logika 2: Blokada dostawy dla wagi > 50 kg.
    [X] Warianty (3 pkt): Wybranie 5 produktów i dodanie im min. 2 wariantów (np. rozmiar, kolor).
    [X] Promocje (3 pkt): Ustawienie promocji cenowych (stara cena -> rabat -> nowa cena) na wybrane produkty.

6. Wygląd i Interfejs (Frontend) (7 pkt + 2 pkt)
    [X] Odwzorowanie wyglądu (7 pkt): Dostosowanie układu, aby był identyczny lub bardzo zbliżony do sklepu źródłowego (układ elementów, niekoniecznie kolory).
    [ ] Estetyka i Standardy (2 pkt): Sklep musi wyglądać profesjonalnie, brak błędów w wyświetlaniu.
    [X] Baner: Dodanie własnego, działającego banera na stronie głównej.
    [X] Strony statyczne: Dostępne strony "O sklepie", "Formy płatności" itp.

7. Testy Automatyczne (Selenium) (5 pkt)
    [ ] Stworzenie skryptu testowego (Python/Java/C# + Selenium).
    [ ] Scenariusz testowy (wykonanie < 5 min):
        [X] Dodanie 10 produktów do koszyka (różne kategorie).
        [X] Wyszukanie produktu po nazwie -> dodanie losowego wyniku do koszyka.
        [X] Usunięcie 3 produktów z koszyka.
        [X] Rejestracja nowego konta.
        [X] Checkout (zamówienie).
        [X] Płatność: Przy odbiorze.
        [X] Wybór jednego z przewoźników.
        [X] Zatwierdzenie zamówienia.
        [X] Sprawdzenie statusu zamówienia.
        [x] Pobranie faktury VAT.

8. Backup i Finalizacja (5 pkt)
    [X] Weryfikacja błędów: Upewnienie się, że nie ma błędów 500, 404, 403 w konsoli/logach.
    [X] Eksport ustawień: Zrzut bazy danych (SQL) oraz plików konfiguracyjnych.
    [ ] Commit finalny: Umieszczenie zrzutu bazy/konfiguracji w folderze /config w repozytorium (umożliwiające odtworzenie sklepu).
