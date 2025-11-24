# Konfiguracja poczty, HTTPS i przewoźników — instrukcja weryfikacji

Poniżej znajduje się podsumowanie zmian, które zostały wprowadzone w sklepie, oraz proste polecenia do weryfikacji.

1) Co zmieniłem w zakresie poczty (e-mail)
- Dodałem i uruchomiłem lokalny dev-sink MailHog (SMTP na porcie `1025`, UI na `8025`).
- Skonfigurowałem ustawienia PrestaShop, aby używał hosta `mailhog:1025` do wysyłki SMTP (z poziomu pliku `ps_configuration` w DB).
- Usunąłem puste wartości użytkownika/hasła SMTP aby uniknąć niepotrzebnej próby autoryzacji.

2) Jak przetestować wysyłkę e-mail (lokalnie)
- Otwórz interfejs MailHog: `http://localhost:8025/` — tutaj pojawią się wszystkie wychodzące wiadomości.
- Przez API MailHog: `curl http://localhost:8025/api/v2/messages` — lista wiadomości w formacie JSON.
- W kontenerze web (wykonaj polecenia z katalogu projektu):
```
docker exec -it prestashop_web bash
php /var/www/html/send_mail_test_direct.php   # powinno zwrócić "true"
php /var/www/html/send_test_debug.php         # uruchamia Mail::send z debugiem
```
- Możesz też w Adminie PrestaShop: `Shop parameters -> General -> Email` i kliknąć "Send test email" — wynik zobaczysz w MailHog.

Dodalem dodatkowo strone dla sprawdzenia listy mailow, w footer dodalem przycisk "MOJE MAILY" ktory pozwala przejrec historie wszystkich mailow

3) Co zostało zrobione w zakresie przewoźników
- Dodano dwóch przewoźników: `DobreWina Kurier A` i `DobreWina Kurier B` (skrypt: `html/create_carriers_and_configure.php`).
- Dla obu przewoźników dodano przedziały cenowe tak, aby przy zamówieniach powyżej 2000 zł dostawa była darmowa.
- Dodałem skrypt `html/add_weight_ranges.php`, który tworzy zakres wagowy dopuszczalny do 50 kg — brak zakresu powyżej 50 kg powoduje, że przewoźnik nie jest dostępny, gdy całkowita waga zamówienia przekroczy 50 kg.
- Opłaty różnią się: Kurier A = 150 zł dla zamówień poniżej progu, Kurier B = 90 zł (oba mają darmową dostawę powyżej 2000 zł).

4) Płatności
- W sklepie zostały ograniczone metody płatności do metod stosowanych w Polsce (brak integracji z zewnętrznymi operatorami). Zmiany wykonano bez przeprowadzania integracji z zewnętrznym providerem.

5) HTTPS (samopodpisany certyfikat)
- W katalogu `prestashop/certs` umieściłem samopodpisany certyfikat oraz klucz (`prestashop.crt`, `prestashop.key`). Pliki są montowane do kontenera web pod `/etc/ssl/private` (konfiguracja w `docker-compose.yml`).
- Po restarcie kontenera serwer WWW powinien obsługiwać połączenia HTTPS na porcie `443` (zauważ, że przeglądarki wyświetlą ostrzeżenie o certyfikacie samopodpisanym — to normalne).

6) Polecenia weryfikacyjne — krok po kroku
- Sprawdź, że MailHog działa i ma wiadomości:
```
curl http://localhost:8025/api/v2/messages | jq '.total'
```
- Wyślij test z poziomu kontenera:
```
docker exec -it prestashop_web bash
php /var/www/html/send_mail_test_direct.php
```
- Sprawdź HTTPS (localhost):
```
# z hosta
curl -vk https://localhost/  # -k pozwala na samopodpisany cert
```
- Sprawdź dostępność przewoźników w bazie:
```
docker exec -it prestashop_db mysql -uprestashop -pprestashop prestashop -e "SELECT id_carrier,name FROM ps_carrier WHERE name LIKE 'DobreWina%';"
```
- Uruchom skrypt, który doda limit wagowy (jeśli nie został jeszcze uruchomiony):
```
docker exec -it prestashop_web bash
php /var/www/html/add_weight_ranges.php
```

7) Uwagi i dalsze kroki
- To środowisko jest przeznaczone do developmentu — do wysyłki produkcyjnej należy skonfigurować zaufanego SMTP (np. dostawca SMTP), a także dostosować polityki bezpieczeństwa.
- Jeśli chcesz, mogę:
  - wygenerować certyfikat z innymi danymi (np. inny CN),
  - skonfigurować prawidłową integrację z konkretnym providerem SMTP (jeśli dasz dane),
  - wygenerować testowe produkty (>1000) dla obciążenia testowego.

---
