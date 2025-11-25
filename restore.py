import subprocess
import os
import shutil
import time

# CONFIG
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PRESTA_HTML_DIR = os.path.join(PROJECT_ROOT, 'prestashop', 'html')
BACKUP_ROOT = os.path.join(PROJECT_ROOT, "backup")

DB_CONTAINER_NAME = "prestashop_db"
DB_USER = "root"
DB_PASS = "prestashop"
DB_NAME = "prestashop"


def list_backups():
    """Zwraca listę folderów w katalogu backup, posortowaną od najnowszej"""
    if not os.path.exists(BACKUP_ROOT):
        return []

    backups = [d for d in os.listdir(BACKUP_ROOT) if os.path.isdir(os.path.join(BACKUP_ROOT, d))]
    backups.sort(reverse=True)
    return backups


def choose_backup():
    """Interfejs wyboru backupu"""
    backups = list_backups()

    if not backups:
        print(f"[BŁĄD] Nie znaleziono żadnych backupów w folderze: {BACKUP_ROOT}")
        exit(1)

    print("\nDOSTĘPNE BACKUPY:")
    for i, folder_name in enumerate(backups):
        print(f" [{i}] {folder_name}")

    print("\nKtórą wersję chcesz przywrócić?")
    while True:
        try:
            choice = input("Wybierz numer (np. 0 dla najnowszego): ")
            index = int(choice)
            if 0 <= index < len(backups):
                return os.path.join(BACKUP_ROOT, backups[index])
            else:
                print("Nieprawidłowy numer.")
        except ValueError:
            print("Podaj liczbę.")


def restore_process(backup_path):
    print(f"\n--- ROZPOCZYNAM PRZYWRACANIE Z: {backup_path} ---")

    sql_file = os.path.join(backup_path, "db_dump.sql")
    zip_file = os.path.join(backup_path, "shop_files.zip")
    config_file = os.path.join(backup_path, "parameters.php")

    if os.path.exists(sql_file):
        print("1. Wgrywanie bazy danych...")
        cmd = [
            "docker", "exec", "-i", DB_CONTAINER_NAME,
            "mysql", "-u", DB_USER, f"-p{DB_PASS}", DB_NAME
        ]
        try:
            with open(sql_file, "r") as infile:
                subprocess.run(cmd, stdin=infile, check=True)
            print("   [SUKCES] Baza przywrócona.")
        except Exception as e:
            print(f"   [BŁĄD] Problem z bazą: {e}")
            return
    else:
        print("   [BŁĄD] Brak pliku db_dump.sql w tym backupie!")

    if os.path.exists(zip_file):
        print("2. Przywracanie plików (themes, modules)...")
        try:
            shutil.unpack_archive(zip_file, PRESTA_HTML_DIR)
            print("   [SUKCES] Pliki rozpakowane.")
        except Exception as e:
            print(f"   [BŁĄD] Nie udało się rozpakować ZIPa: {e}")
    else:
        print("   [OSTRZEŻENIE] Brak pliku shop_files.zip")

    if os.path.exists(config_file):
        print("3. Przywracanie parameters.php...")
        dest_path = os.path.join(PRESTA_HTML_DIR, "app/config/parameters.php")
        try:
            shutil.copy2(config_file, dest_path)
            print("   [SUKCES] Config przywrócony.")
        except Exception as e:
            print(f"   [BŁĄD] Kopiowanie configu: {e}")

    print("4. Czyszczenie cache PrestaShop...")
    subprocess.run(["docker", "exec", "prestashop_web", "rm", "-rf", "/var/www/html/var/cache/prod"],
                   stderr=subprocess.DEVNULL)
    subprocess.run(["docker", "exec", "prestashop_web", "rm", "-rf", "/var/www/html/var/cache/dev"],
                   stderr=subprocess.DEVNULL)
    print("   [SUKCES] Cache wyczyszczony.")


if __name__ == "__main__":
    print("=" * 50)
    print("NARZĘDZIE PRZYWRACANIA BACKUPU (RESTORE)")
    print("=" * 50)

    if not os.path.exists(PRESTA_HTML_DIR):
        print("[BŁĄD] brak folderu prestashop/html")
        exit(1)

    selected_backup_path = choose_backup()

    print(f"\nUWAGA! Zamierzasz nadpisać obecny sklep danymi z: {os.path.basename(selected_backup_path)}")
    confirm = input("Wpisz 'TAK' aby kontynuować: ")

    if confirm.strip().upper() == "TAK":
        restore_process(selected_backup_path)
        print("\n" + "=" * 50)
        print("GOTOWE! Odśwież stronę sklepu.")
    else:
        print("Anulowano.")