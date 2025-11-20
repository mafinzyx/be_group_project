# Electronic Business Group Project

PrestaShop 1.7.8 implementation using Docker

## Requirements

- Docker
- Docker Compose

### How to install Docker & Docker Compose

1.  **Update your package list:**
    ```bash
    sudo apt update
    ```

2.  **Install Docker and Compose:**
    ```bash
    sudo apt install -y docker.io docker-compose
    ```

3.  **Fix permissions (so you don't have to use 'sudo' every time):**
    ```bash
    sudo usermod -aG docker $USER
    ```

4.  **IMPORTANT:** Restart your computer to make it work.

## Installation

1. **Clone the repository**
    ```bash
    git clone https://github.com/mafinzyx/be_group_project.git
    cd ./be_group_project
    ```

2. **Generate SSL certificates**
    ```bash
    mkdir -p certs
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout certs/prestashop.key -out certs/prestashop.crt
    ```
    **Important:** When prompted for "Common Name (CN)", enter: localhost. Skip other fields by pressing Enter.

3. **Start the environment**
    ```bash
    docker-compose up -d
    ```
    Usually this takes me around up to a minute, first startup takes longer.

    **If you are getting "python" errors** try using:
    ```bash
    sudo apt install python3-setuptools
    ```
    and then use `docker-compose up -d` again.

    After generating the base files use this command to fix the access to files

    ```bash
    sudo chmod -R 777 html
    ```

    If you ever need to reset docker or the database use this:
    ```bash
    docker-compose down -v
    docker-compose up -d
    ```

4. **Working on the project**\
    If you've made some changes on the websites panel or you've added products to the website, you need to update `init.sql` with this command, before pushing changes to git.

    ```
    sudo docker exec prestashop_db mysqldump -u root -pprestashop prestashop > dumps/init.sql
    ```

    ```
    git add .
    git commit -m "Changes to XYZ"
    git push
    ```
    if some changes aren't getting uploaded, check `.gitignore` file.

5. **First time accessing the shop**\
    After starting the environment go to http://localhost:80 


## Login information

PrestaShop login information:\
email: ```prestashop@prestashop.com```\
password: ```prestashop```

Database login information:\
login: ```prestashop```\
password: ```prestashop```

Configuration information in `docker-compose.yml`

## Authors

[![GitHub - Danylo Zherzdiev](https://img.shields.io/badge/GitHub-Danylo_Zherzdiev-181717?style=for-the-badge&logo=github)](https://github.com/mafinzyx)   [![GitHub - Danylo Lohachov](https://img.shields.io/badge/GitHub-Danylo_Lohachov-181717?style=for-the-badge&logo=github)](https://github.com/eternaki) [![GitHub - Maciej Blawat](https://img.shields.io/badge/GitHub-Maciej_Blawat-181717?style=for-the-badge&logo=github)](https://github.com/maciejblawat) [![GitHub - Maciej Blawat](https://img.shields.io/badge/GitHub-Mateusz_Grzonka-181717?style=for-the-badge&logo=github)]([https://github.com/maciejblawat](https://github.com/mateushhh)) [![GitHub - Maria Volkova](https://img.shields.io/badge/GitHub-Maria_Volkova-181717?style=for-the-badge&logo=github)](https://github.com/mvollkova)
