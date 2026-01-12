FROM prestashop/prestashop:1.7.8

COPY ./html/themes /var/www/html/themes
COPY ./html/img /var/www/html/img
COPY ./html/modules /var/www/html/modules
#maile
COPY ./html/mymails.php /var/www/html/mymails.php

#parametry
COPY parameters_prod.php /var/www/html/app/config/parameters.php

#usuniecie instalacji
RUN rm -rf /var/www/html/install

RUN chown -R www-data:www-data \
    /var/www/html/themes \
    /var/www/html/img \
    /var/www/html/modules \
    /var/www/html/mymails.php \
    /var/www/html/app/config/parameters.php