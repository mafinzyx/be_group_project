# Używamy oficjalnego obrazu jako bazy
FROM prestashop/prestashop:1.7.8

# Kopiujemy zawartość bieżącego katalogu (czyli folderu prestashop) do obrazu
# Dzięki temu Twoje moduły i zmiany w kodzie trafią do obrazu
COPY . /var/www/html

# Naprawiamy uprawnienia (kluczowe, żeby nie było błędu 500 na produkcji)
RUN chown -R www-data:www-data /var/www/html
RUN chmod -R 777 /var/www/html/var

# Informujemy, że kontener nasłuchuje na porcie 80
EXPOSE 80