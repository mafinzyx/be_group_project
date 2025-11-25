import subprocess
import os
import shutil
from datetime import datetime

# --- CONFIG ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PRESTA_HTML_DIR = os.path.join(PROJECT_ROOT, 'prestashop', 'html')
BACKUP_ROOT = os.path.join(PROJECT_ROOT, "backup")
BACKUP_DIR = os.path.join(BACKUP_ROOT, datetime.now().strftime("%Y%m%d"))

DB_CONTAINER_NAME = "prestashop_db"
DB_USER = "root"
DB_PASS = "prestashop"
DB_NAME = "prestashop"

FOLDERS_TO_ZIP = [
    "themes",
    "modules",
    "override",
]

FILE_PARAMETERS = "app/config/parameters.php"


def init_backup_dir():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        print(f"[INFO] Utworzono folder na backup: {BACKUP_DIR}")


def backup_database_docker():
    print(f"\n--- 1. EKSPORT BAZY DANYCH (Z KONTENERA DOCKER) ---")
    output_file = os.path.join(BACKUP_DIR, "db_dump.sql")

    cmd = [
        "docker", "exec", DB_CONTAINER_NAME,
        "mysqldump", "-u", DB_USER, f"-p{DB_PASS}", DB_NAME
    ]

    try:
        with open(output_file, "w") as outfile:
            subprocess.run(cmd, stdout=outfile, check=True)
        print(f"[SUKCES] Baza danych zapisana w: {output_file}")
    except Exception as e:
        print(f"[BŁĄD] Nie udało się wykonać zrzutu bazy : {e}")


def backup_files_local():
    print(f"\n--- 2. BACKUP PLIKÓW KONFIGURACYJNYCH I MODUŁÓW ---")

    # kopiowanie parameters.php
    param_src = os.path.join(PRESTA_HTML_DIR, FILE_PARAMETERS)
    param_dst = os.path.join(BACKUP_DIR, "parameters.php")

    if os.path.exists(param_src):
        shutil.copy2(param_src, param_dst)
        print(f"[SUKCES] Skopiowano plik konfiguracyjny (parameters.php)")
    else:
        print(f"[OSTRZEŻENIE] Nie znaleziono pliku {FILE_PARAMETERS} w {param_dst}")

    # pakowanie do zipa
    zip_path = os.path.join(BACKUP_DIR, "shop_files")
    temp_dir = os.path.join(BACKUP_DIR, "temp_zip_content")

    if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    files_found = False
    print(f"   -> Przygotowywanie plików do spakowania...")

    for folder in FOLDERS_TO_ZIP:
        src = os.path.join(PRESTA_HTML_DIR, folder)
        dst = os.path.join(temp_dir, folder)

        if os.path.exists(src):
            try:
                shutil.copytree(src, dst)
                print(f"      + Dodano folder: {folder}")
                files_found = True
            except Exception as e:
                print(f"      [!] Błąd przy kopiowaniu {folder}: {e}")
        else:
            print(f"      [!] Folder nie istnieje: {folder}")

    if files_found:
        print(f"   -> Kompresowanie ...")
        shutil.make_archive(zip_path, 'zip', temp_dir)
        print(f"[SUKCES] Utworzono archiwum: shop_files.zip")
    else:
        print("[INFO] Nie znaleziono plików do spakowania w folderze themes/modules/override.")

    if os.path.exists(temp_dir): shutil.rmtree(temp_dir)


if __name__ == "__main__":
    print("=" * 50)
    print(f"AUTOMATYCZNY BACKUP SKLEPU (DOCKER)")
    print("=" * 50)

    if not os.path.exists(PRESTA_HTML_DIR):
        print(f"[blad] brak folderu z plikami sklepu w: {PRESTA_HTML_DIR}")
        print("skrypt powinien byc w glownym folderze projektu")
        exit(1)

    init_backup_dir()
    backup_database_docker()
    backup_files_local()

    print("\n" + "=" * 50)
    print("PROCES ZAKOŃCZONY")
    print(f"Pliki exportu znajduja sie w:\n{BACKUP_DIR}")
    print("=" * 50)