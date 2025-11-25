import subprocess
import os
import shutil
from datetime import datetime

# --- CONFIG ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PRESTA_HTML_DIR = os.path.join(PROJECT_ROOT, 'prestashop', 'html')
BACKUP_ROOT = os.path.join(PROJECT_ROOT, "backup")

DATE_STR = datetime.now().strftime("%Y%m%d")
TEMP_BACKUP_DIR = os.path.join(BACKUP_ROOT, f"temp_{DATE_STR}")

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
    if not os.path.exists(BACKUP_ROOT):
        os.makedirs(BACKUP_ROOT)

    if os.path.exists(TEMP_BACKUP_DIR):
        shutil.rmtree(TEMP_BACKUP_DIR)
    os.makedirs(TEMP_BACKUP_DIR)
    print(f"[INFO] Utworzono folder roboczy: {TEMP_BACKUP_DIR}")


def backup_database_docker():
    print(f"\n--- 1. EKSPORT BAZY DANYCH ---")
    output_file = os.path.join(TEMP_BACKUP_DIR, "db_dump.sql")

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
    print(f"\n--- 2. BACKUP PLIKÓW ---")

    # A. Kopiowanie parameters.php
    param_src = os.path.join(PRESTA_HTML_DIR, FILE_PARAMETERS)
    param_dst = os.path.join(TEMP_BACKUP_DIR, "parameters.php")

    if os.path.exists(param_src):
        shutil.copy2(param_src, param_dst)
        print(f"[SUKCES] Skopiowano parameters.php")
    else:
        print(f"[OSTRZEŻENIE] Brak pliku {FILE_PARAMETERS}")

    inner_zip_path = os.path.join(TEMP_BACKUP_DIR, "shop_files")
    temp_content_dir = os.path.join(TEMP_BACKUP_DIR, "content_tmp")

    os.makedirs(temp_content_dir)

    files_found = False
    print(f"   -> Zbieranie plików (modules, themes, override)...")

    for folder in FOLDERS_TO_ZIP:
        src = os.path.join(PRESTA_HTML_DIR, folder)
        dst = os.path.join(temp_content_dir, folder)

        if os.path.exists(src):
            try:
                shutil.copytree(src, dst)
                files_found = True
            except Exception as e:
                print(f"      [!] Błąd przy kopiowaniu {folder}: {e}")

    if files_found:
        print(f"   -> Tworzenie wewnętrznego archiwum shop_files.zip ...")
        shutil.make_archive(inner_zip_path, 'zip', temp_content_dir)
        print(f"[SUKCES] Utworzono shop_files.zip")
    else:
        print("[INFO] Brak plików do spakowania.")

    shutil.rmtree(temp_content_dir)


def finalize_backup():
    print(f"\n--- 3. FINALIZACJA (PAKOWANIE CAŁOŚCI) ---")
    final_zip_name = os.path.join(BACKUP_ROOT, DATE_STR)

    try:
        print(f"   -> Tworzenie głównego pliku: {DATE_STR}.zip ...")
        shutil.make_archive(final_zip_name, 'zip', TEMP_BACKUP_DIR)

        shutil.rmtree(TEMP_BACKUP_DIR)
        print(f"[SUKCES] Backup gotowy: {final_zip_name}.zip")
        return f"{final_zip_name}.zip"
    except Exception as e:
        print(f"[BŁĄD] Nie udało się stworzyć finalnego ZIPa: {e}")
        return None


if __name__ == "__main__":
    print("=" * 50)
    print(f"AUTOMATYCZNY BACKUP SKLEPU (ZIP)")
    print("=" * 50)

    if not os.path.exists(PRESTA_HTML_DIR):
        print(f"[BŁĄD] Brak folderu z plikami sklepu: {PRESTA_HTML_DIR}")
        exit(1)

    init_backup_dir()
    backup_database_docker()
    backup_files_local()
    final_path = finalize_backup()

    print("\n" + "=" * 50)
    if final_path:
        print(f"BACKUP ZAKOŃCZONY POMYŚLNIE.")
        print(f"Plik: {final_path}")
    else:
        print("BACKUP ZAKOŃCZONY BŁĘDEM.")
    print("=" * 50)