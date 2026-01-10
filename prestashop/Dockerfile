FROM dobrewina/prestashop:latest

COPY ./html/themes /var/www/html/themes
COPY ./html/img /var/www/html/img
COPY ./html/modules /var/www/html/modules
COPY ./htmlmymails.php /var/www/html/mymails.php

RUN chown -R www-data:www-data /var/www/html/themes /var/www/html/img /var/www/html/modules /var/www/html/admin191rnbbnl /var/www/html/mymails.php