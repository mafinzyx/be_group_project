# Projekt Zespołowy Biznes Elektroniczny PART2

# WAŻNE
### Klaster
**NazwaKlastra:** `BE_196610` \
**Port:** `196610`
### Baza danych
Nie stawiamy własnego kontenera MySQL w `docker-compose` tylko musimy użyć wspólnego na serwera MySQL \
**NazwaBazy:** `BE_196610` \
**Port:** `3306` \
Można wejść na przeglądarkowy podgląd bazy danych na **Port:** `9099`

# VPN
**- Instrukcja konfiguracji OpenVPN z VPN ETI** -> http://starter.eti.pg.gda.pl/openvpn/ \
**DO POBRANIA:** \
**- Instalator OpenVPN** -> https://openvpn.net/community/ \
**- Konfiguracja vpn2023.zip** -> http://starter.eti.pg.gda.pl/openvpn/download/vpn2023.zip

## Przygotowanie połączenia VPN
1. Wypakować pliki z `vpn2023.zip`
2. Przejść do folderu gdzie zainstalowaliśmy openvpn (u mnie `D:\openvpn`) potem do folderu config
3. Do folderu config wrzucić rozpakowane wcześniej pliki (nie plik .zip tylko jego zawartość)
4. Po uruchomieniu programu OpenVPN, na pasku zadań w prawym dolnym rogu powinna się wyświetlać ikonka programu.
5. Klikamy na niego prawym przyciskiem myszy i klikamy Połącz, podajemy dane do logowania się takie jak na mojapg i jesteśmy połączeni.

**WAŻNE!**
Należy podać cały login w postaci: `s123456@student.pg.edu.pl`

# SSH
**DO POBRANIA** \
**Instalator PuTTY (klient SSH)** -> https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html \
*można korzystać z terminala na windowsie po prostu, ale PuTTY pozwala na tunelowanie które będzie potem potrzebne. \
**na Linux/macOS powinno wystarczyć terminalowe SSH

## Łączenie z Bastionem (`172.20.83.101`)
1. Połącz się z VPN wydziałowym (OpenVPN)
2. Zaloguj się na Bastion (SSH) \
W PuTTY: \
**Host Name (or IP adress)**: `172.20.83.101` \
W terminalu który się wyświetli \
**Login**: `rsww`
**Password**: `qwe123`
4. Z bastiona logujemy się na węzeł klastra:
`ssh hdoop@student-swarm01.maas` \
jeśli będzie pytanie o hasło to wpisujesz `qwe123`

**WAŻNE** Jeśli chcecie kopiować linijki do okienka terminala, skopiujcie tekst a potem prawym przyciskiem myszy na okienko, wszystko powinno się wkleić

# Baza Danych MySQL

## Łączenie z Bazą Danych
1. Połącz się z VPN wydziałowym (OpenVPN)
2. W PuTTY Host: `172.20.83.101` (nie łączymy się jeszcze)
3. Wchodzimy w zakładke Connection -> SSH -> Tunnels i uzupełniamy dane \
Source Port: `9099` \
Destination: `student-swarm01.maas:9099` 
4. Klikamy Add i Open.
5. Zaloguj się \
login: `rsww` \
hasło: `qwe123`
6. Otwórz bazę przez przeglądarkę, wejdź na `http://localhost:9099` \
Username: `root` \
Password: `student`

## Importowanie `init.sql`
1. Łączymy się z bazą danych według poprzedniej instrukcji
2. Klikamy zakładke "Import", wrzucamy plik init.sql` \
**ROZWIĄZANIE BŁĘDU** "*Error in query (1273): Unknown collation: 'utf8mb4_0900_ai_ci'*"
3. Otwórz init.sql w edytorze tekstu, wciśnij CTRL+H zamień wszystkie `utf8mb4_0900_ai_ci` na `utf8mb4_general_ci`
4. Spróbuj ponownie zaimportować `init.sql`

## Zarządzanie klastrem (na serwerze)
- `ssh hdoop@student-swarm01.maas`
- `/opt/storage/actina15-20/block-storage/students/projects/students-swarm-services/BE_196610` Ścieżka folderu na klastrze (tu znajduje się `docker-compose.yml`)
- `docker service ls | grep BE_196610` - Listowanie usługi w klastrze żeby sprawdzić status REPLICAS 1/1 -> działa 0/1 błąd configu / brak zasobów
- `docker stack deploy -c docker-compose.yml BE_196610 --with-registry-auth` wysyła docker-compose.yml do klastra
- `docker service ps BE_196610_prestashop --no-trunc` pokazuje historię zadań dla danej usługi
- `docker service rm BE_196610_prestashop` - Całkowicie usuwa usługę z klastra. 

## Praca z kontenerem
- `docker ps | grep BE_196610` - Szuka ID konkretnego działającego kontenera na serwerze.
- `docker exec -it ID_KONTENERA /bin/bash` Otwiera terminal wewnątrz kontenera
- `/var/www/html/app/config/parameters.php` ścieżka do `parameters.php` wewnątrz kontenera
- `rm -rf var/cache/*` - Czyszczenie cache prestashopu, obowiązkowe po każdej zmianie w parameters.php

## Konfiguracja PuTTY do wchodzenia na strone i na baze
- Host Name `172.20.83.101`
- Przejdź do SSH/Tunnels
- Source Port: 8080
- Destination student-swarm01.maas:19661
- Add
- Source Port: 9099
- Destination student-swarm01.maas:9099
- Teraz po zalogowaniu się można wejść na localhost:8080 i mamy dostęp do strony a localhost:9099 daje dostęp do bazy danych

## Pliki konfiguracyjne
Tutaj na branchu powinny być dwa pliki konfiguracyjne niezbędne do pracy `docker-compose.yml` oraz `parameters.php` długo mi zajęło skonfigurowanie ich w sposób żeby działały.

## PART 2:
[x] Added GoogleAnalytics:
    Gmail Account ([https://analytics.google.com/](https://analytics.google.com/)): 
    
        Email: dobrewina5@gmail.com
        Password: dobreWina5_PG

## Authors

[![GitHub - Danylo Zherzdiev](https://img.shields.io/badge/GitHub-Danylo_Zherzdiev-181717?style=for-the-badge&logo=github)](https://github.com/mafinzyx)
[![GitHub - Danylo Lohachov](https://img.shields.io/badge/GitHub-Danylo_Lohachov-181717?style=for-the-badge&logo=github)](https://github.com/eternaki)
[![GitHub - Maciej Blawat](https://img.shields.io/badge/GitHub-Maciej_Blawat-181717?style=for-the-badge&logo=github)](https://github.com/maciejblawat)
[![GitHub - Mateusz Grzonka](https://img.shields.io/badge/GitHub-Mateusz_Grzonka-181717?style=for-the-badge&logo=github)](https://github.com/mateushhh)
[![GitHub - Maria Volkova](https://img.shields.io/badge/GitHub-Maria_Volkova-181717?style=for-the-badge&logo=github)](https://github.com/mvollkova)

198023 - Mateusz Grzonka
197844 - Maciej Bławat
196765 - Danylo Zherzdiev
196610 - Danylo Lohachov
196660 - Maria Volkova
