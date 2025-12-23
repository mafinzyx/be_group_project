## PART 2:
[x] Added GoogleAnalytics:
    Gmail Account ([https://analytics.google.com/](https://analytics.google.com/)): 
    
        Email: dobrewina5@gmail.com
        Password: dobreWina5_PG

[x] (3 pkt) W kompozycji zdefiniowano ograniczenia górne na zasoby sprzętowe dla poszczególnych usług tj. vCore oraz ilość dostępnej pamięci RAM per usługa.
    Jak sprawdzic: 
    
        cd prestashop
        docker stats --no-stream

        LIMIT 512 dla prestashop_web/db oraz 256 dla mailhog
        CONTAINER ID   NAME             CPU %     MEM USAGE / LIMIT   MEM %     NET I/O           BLOCK IO       PIDS
        4a5522c3dd41   prestashop_web   0.01%     103.9MiB / 512MiB   20.30%    1.14MB / 1.09MB   0B / 1.09MB     11
        b7299c767c0d   prestashop_db    0.11%     227MiB / 512MiB     44.34%    220kB / 943kB     770kB / 483MB   29
        ec3f4168aef8   mailhog          0.00%     1.66MiB / 256MiB    0.65%     11.2kB / 126B     0B / 0B         5

Docker Hub: 

    UNIKALNY PORT - 19661
    PREFIX - BE_196610
