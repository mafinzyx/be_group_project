## PART 2:
### Credentials:
Gmail Account ([https://analytics.google.com/](https://analytics.google.com/)): 
    
    Email: dobrewina5@gmail.com
    Password: dobreWina5_PG

Docker Hub ([https://hub.docker.com](https://hub.docker.com)):

    Email: dobrewina5@gmail.com
    Password: dobreWina5_PG


## DONE?
[x] (5 pkt) * Sklep zintegrowano z usługą Google Analytics. W portalu GA utworzono nową witrynę do monitorowania. Podczas prezentacji GA powinno zawierać dane dotyczące historii odwiedzin sklepu, a także informacje o wartości złożonych zamówień. Informacje powinny rejestrowane co najmniej od 48 godzin.

[x] (5 pkt) W Google Analytics zdefiniowano dwa mierzalne cele: typu „destination” oraz typu „event”. 

    Dla celu typu „destination” należy zdefiniować osiągnięcie przez użytkownika strony po naciśnięciu przycisku rejestracji. 
    Dla celu typu „event” należy zdefiniować własny typ eventu (i zarejestrować go w GA), który będzie emitowany przez sklep podczas korzystania z baneru lub podczas dodawania przez użytkownika do koszyka produktów w promocji. Po stronie sklepu zaimplementowano emitowanie zdefiniowanych eventów. 
    Zespół potrafi zaprezentować w panelu GA historię osiągnięcia obydwu zdefiniowanych celów.


[x] (3 pkt) W kompozycji zdefiniowano ograniczenia górne na zasoby sprzętowe dla poszczególnych usług tj. vCore oraz ilość dostępnej pamięci RAM per usługa.
    Jak sprawdzic: 
    
        cd prestashop
        docker stats --no-stream

        LIMIT 512 dla prestashop_web/db oraz 256 dla mailhog
        CONTAINER ID   NAME             CPU %     MEM USAGE / LIMIT   MEM %     NET I/O           BLOCK IO       PIDS
        4a5522c3dd41   prestashop_web   0.01%     103.9MiB / 512MiB   20.30%    1.14MB / 1.09MB   0B / 1.09MB     11
        b7299c767c0d   prestashop_db    0.11%     227MiB / 512MiB     44.34%    220kB / 943kB     770kB / 483MB   29
        ec3f4168aef8   mailhog          0.00%     1.66MiB / 256MiB    0.65%     11.2kB / 126B     0B / 0B         5

[x] (5 pkt) Zespół przygotował w ramach źródeł projektu plik konfiguracyjny pipeline wyzwalany automatycznie po zdarzeniu push do gałęzi master/main. W wyniku działania pipeline tworzony jest obraz sklepu.
Mozna sprawdzic przez Docker Hub -> My profile -> Repositories -> dobrewina/prestashop

[?] (5 pkt) Zespół przygotował kompozycję i dodatkowe skrypty w taki sposób, aby zawartość bazy danych była automatycznie inicjowana podczas uruchamiania kompozycji. Po zainicjowaniu bazy danych, sklep jest gotowy do działania i spełnia minimalne wymagania funkcjonalne wskazane w etapie 1.

### TODO

[] (5 pkt) * Sklep został wdrożony na klastrze i posiada funkcjonalność określoną co najmniej jako minimalne wymagania określone w etapie I. Sklep korzysta z bazy danych utworzonej na wspólnym serwerze bazodanowym dostępnym w klastrze.

[] (5 pkt) * Zespół utworzył niezbędne pliki Dockerfile oraz plik kompozycji docker-compose.yml, który umożliwia automatyczne wdrożenie sklepu na klastrze studenckim. Kompozycja wykorzystuje jedynie wcześniej zbudowane obrazy, opublikowane w publicznym rejestrze. Utworzona kompozycja została wykorzystana w celu wdrożenia sklepu na klastrze studenckim. Zespół uruchomił dokładnie jeden stack na klastrze i spełnia on wymagania w zakresie nazewnictwa i numerów portów.

[] (5 pkt) * Skrypt wykonujący testy automatyczne działa prawidłowo na sklepie wdrożonym w klastrze.

[] (2 pkt) Sklep ma włączony cache podczas prezentacji;