import subprocess
import os
import shutil
import time

# --- CONFIG ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PRESTA_HTML_DIR = os.path.join(PROJECT_ROOT, 'prestashop', 'html')
BACKUP_ROOT = os.path.join(PROJECT_ROOT, "backup")

RESTORE_TEMP_DIR = os.path.join(BACKUP_ROOT, "restore_temp")

DB_CONTAINER_NAME = "prestashop_db"
DB_USER = "root"
DB_PASS = "prestashop"
DB_NAME = "prestashop"


def list_backups():
    """Zwraca listę plików .zip w katalogu backup"""
    if not os.path.exists(BACKUP_ROOT):
        return []

    # Szukamy tylko plików kończących się na .zip
    backups = [f for f in os.listdir(BACKUP_ROOT)
               if f.endswith('.zip') and os.path.isfile(os.path.join(BACKUP_ROOT, f))]
    backups.sort(reverse=True)
    return backups


def choose_backup():
    """Interfejs wyboru backupu"""
    backups = list_backups()

    if not backups:
        print(f"[BŁĄD] Nie znaleziono żadnych plików .zip w folderze: {BACKUP_ROOT}")
        exit(1)

    print("\nDOSTĘPNE BACKUPY (ZIP):")
    for i, file_name in enumerate(backups):
        print(f" [{i}] {file_name}")

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


def prepare_restore_files(zip_path):
    """Rozpakowuje główny ZIP do folderu tymczasowego"""
    print(f"\n--- PRZYGOTOWANIE PLIKÓW ---")

    if os.path.exists(RESTORE_TEMP_DIR):
        shutil.rmtree(RESTORE_TEMP_DIR)
    os.makedirs(RESTORE_TEMP_DIR)

    print(f"   -> Rozpakowywanie {os.path.basename(zip_path)} do folderu roboczego...")
    try:
        shutil.unpack_archive(zip_path, RESTORE_TEMP_DIR)
        return True
    except Exception as e:
        print(f"[BŁĄD] Nie udało się rozpakować archiwum: {e}")
        return False


def restore_process():
    print(f"\n--- ROZPOCZYNAM PRZYWRACANIE ---")

    # Ścieżki wewnątrz rozpakowanego folderu roboczego
    sql_file = os.path.join(RESTORE_TEMP_DIR, "db_dump.sql")
    zip_files_shop = os.path.join(RESTORE_TEMP_DIR, "shop_files.zip")
    config_file = os.path.join(RESTORE_TEMP_DIR, "parameters.php")

    # 1. BAZA DANYCH
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
        print("   [BŁĄD] Brak pliku db_dump.sql w backupie!")

    # 2. PLIKI SKLEPU
    if os.path.exists(zip_files_shop):
        print("2. Przywracanie plików (themes, modules)...")
        try:
            shutil.unpack_archive(zip_files_shop, PRESTA_HTML_DIR)
            print("   [SUKCES] Pliki rozpakowane.")
        except Exception as e:
            print(f"   [BŁĄD] Nie udało się rozpakować wewnętrznego ZIPa: {e}")
    else:
        print("   [OSTRZEŻENIE] Brak pliku shop_files.zip wewnątrz backupu.")

    # 3. CONFIG
    if os.path.exists(config_file):
        print("3. Przywracanie parameters.php...")
        dest_path = os.path.join(PRESTA_HTML_DIR, "app/config/parameters.php")
        try:
            shutil.copy2(config_file, dest_path)
            print("   [SUKCES] Config przywrócony.")
        except Exception as e:
            print(f"   [BŁĄD] Kopiowanie configu: {e}")

    # 4. CACHE
    print("4. Czyszczenie cache PrestaShop...")
    subprocess.run(["docker", "exec", "prestashop_web", "rm", "-rf", "/var/www/html/var/cache/prod"],
                   stderr=subprocess.DEVNULL)
    subprocess.run(["docker", "exec", "prestashop_web", "rm", "-rf", "/var/www/html/var/cache/dev"],
                   stderr=subprocess.DEVNULL)
    print("   [SUKCES] Cache wyczyszczony.")


def cleanup():
    """Usuwa folder tymczasowy"""
    if os.path.exists(RESTORE_TEMP_DIR):
        print("\n--- SPRZĄTANIE ---")
        shutil.rmtree(RESTORE_TEMP_DIR)
        print("   [OK] Folder roboczy usunięty.")


if __name__ == "__main__":
    print("=" * 50)
    print("NARZĘDZIE PRZYWRACANIA BACKUPU (ZIP RESTORE)")
    print("=" * 50)

    if not os.path.exists(PRESTA_HTML_DIR):
        print("[BŁĄD] brak folderu prestashop/html")
        exit(1)

    selected_backup_zip = choose_backup()

    print(f"\nUWAGA! Zamierzasz nadpisać obecny sklep danymi z: {os.path.basename(selected_backup_zip)}")
    confirm = input("Wpisz 'TAK' aby kontynuować: ")

    if confirm.strip().upper() == "TAK":
        if prepare_restore_files(selected_backup_zip):
            restore_process()
            cleanup()

            print("\n" + "=" * 50)
            print("GOTOWE! Odśwież stronę sklepu.")
    else:
        print("Anulowano.")