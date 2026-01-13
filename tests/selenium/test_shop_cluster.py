import os
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from random import randint, choice
from time import sleep

# --- KONFIGURACJA ---
BASE_URL = "http://localhost:8080"

def create_driver():
    options = webdriver.FirefoxOptions()
    service = Service()

    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--ignore-ssl-errors")

    # Ustawienia do automatycznego pobierania faktur PDF
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.dir", os.getcwd())
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
    options.set_preference("pdfjs.disabled", True)

    driver = webdriver.Firefox(service=service, options=options)
    driver.set_window_size(1400, 900)
    driver.implicitly_wait(5)
    return driver


def registration_test(driver, email):
    print("KROK: Rejestracja nowego klienta...")
    driver.get(f"{BASE_URL}/index.php?controller=authentication&create_account=1")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "field-firstname")))

    driver.find_element(By.ID, "field-id_gender-1").click()
    driver.find_element(By.ID, "field-firstname").send_keys("Jan")
    driver.find_element(By.ID, "field-lastname").send_keys("Testowy")
    driver.find_element(By.ID, "field-email").send_keys(email)
    driver.find_element(By.ID, "field-password").send_keys("Haslo123!")
    driver.find_element(By.ID, "field-birthday").send_keys("1990-01-01")

    # Klikamy checkboxy (tylko te widoczne/wymagane)
    checkboxes = ["optin", "customer_privacy", "psgdpr"]
    for name in checkboxes:
        try:
            driver.find_element(By.NAME, name).click()
        except:
            pass

    # Przycisk zapisu
    try:
        button = driver.find_element(By.CSS_SELECTOR, "button[data-link-action='save-customer']")
    except:
        button = driver.find_element(By.CSS_SELECTOR, ".btn.btn-primary.form-control-submit")

    button.click()

    # Czekamy na przekierowanie po rejestracji
    WebDriverWait(driver, 20).until(lambda d: "create_account=1" not in d.current_url)
    print("-> Rejestracja zakończona sukcesem")


def add_products_test(driver, category_link, num_products):
    print(f"KROK: Dodawanie {num_products} produktów z: {category_link}")
    driver.get(category_link)

    # Czekamy na listę produktów
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, '#js-product-list')))

    products = driver.find_elements(By.CSS_SELECTOR, '.thumbnail.product-thumbnail')
    product_links = [p.get_attribute("href") for p in products]

    added_counter = 0

    # Iterujemy po linkach (żeby ominąć niedostępne)
    for link in product_links:
        if added_counter >= num_products:
            break

        driver.get(link)

        try:
            # Szukamy przycisku dodawania (krótki timeout 2s - jak nie ma, to produkt niedostępny)
            add_btn_selector = (By.CSS_SELECTOR, '.btn.btn-primary.add-to-cart')
            WebDriverWait(driver, 2).until(EC.element_to_be_clickable(add_btn_selector))

            # --- WYMÓG: RÓŻNE ILOŚCI ---
            qty = randint(1, 2)

            qty_input = driver.find_element(By.ID, 'quantity_wanted')
            qty_input.send_keys(Keys.CONTROL + "a")
            qty_input.send_keys(Keys.DELETE)
            qty_input.send_keys(str(qty))

            driver.find_element(*add_btn_selector).click()

            # Czekamy na modal potwierdzający
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "blockcart-modal")))

            print(f"-> Dodano: {link} (Ilość: {qty})")
            added_counter += 1

        except (TimeoutException, NoSuchElementException) as e:
            # Produkt niedostępny -> idziemy do następnego
            print(f"-> Pominięto produkt (niedostępny lub brak przycisku): {link}")
            continue

    print(f"-> Pomyślnie dodano {added_counter} produktów.")


def find_by_name_test(driver, search_term):
    print(f"KROK: Wyszukiwanie frazy '{search_term}' i wybór losowego produktu...")
    driver.get(BASE_URL)

    search_bar = driver.find_element(By.CSS_SELECTOR, '#search_widget input[type="text"]')
    search_bar.clear()
    search_bar.send_keys(search_term)
    search_bar.send_keys(Keys.ENTER)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'js-product-list')))

    # Pobieramy wszystkie znalezione produkty
    products = driver.find_elements(By.CSS_SELECTOR, '.thumbnail.product-thumbnail')
    product_links = [p.get_attribute("href") for p in products]

    if product_links:
        # --- WYMÓG: LOSOWY PRODUKT ---
        # Próbujemy dodać do 5 losowych produktów (na wypadek jeśli niektóre niedostępne)
        max_attempts = min(5, len(product_links))

        for attempt in range(max_attempts):
            try:
                link = choice(product_links)
                print(f"-> Wylosowano produkt (próba {attempt+1}/{max_attempts}): {link}")

                driver.get(link)

                # Dodajemy do koszyka (timeout 2s - jeśli niedostępny, próbujemy następny)
                add_btn = WebDriverWait(driver, 2).until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '.btn.btn-primary.add-to-cart')))
                add_btn.click()

                WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "blockcart-modal")))
                print("-> Produkt z wyszukiwania dodany.")
                return  # Sukces - wychodzimy

            except (TimeoutException, NoSuchElementException):
                print(f"-> Produkt niedostępny, próbuję następny...")
                continue

        # Jeśli wszystkie próby nie powiodły się
        print(f"BŁĄD: Nie udało się dodać żadnego produktu po {max_attempts} próbach")
    else:
        print(f"BŁĄD: Nie znaleziono żadnych produktów dla frazy '{search_term}'")


def add_address_test(driver):
    print("KROK: Dodawanie adresu do profilu...")
    driver.get(f"{BASE_URL}/index.php?controller=address")

    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "field-address1")))
    driver.find_element(By.ID, "field-address1").send_keys("ul. Sezamkowa 1")
    driver.find_element(By.ID, "field-postcode").send_keys("80-180")
    driver.find_element(By.ID, "field-city").send_keys("Gdańsk")

    # Zapisujemy adres
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    # Czekamy na przekierowanie
    WebDriverWait(driver, 20).until(lambda d: "address" not in d.current_url or "addresses" in d.current_url)
    print("-> Adres dodany do profilu")


def remove_from_cart_test(driver):
    print("KROK: Usuwanie 3 produktów z koszyka...")
    driver.get(f"{BASE_URL}/index.php?controller=cart")

    for i in range(3):
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'cart-item')))
            cart_items = driver.find_elements(By.CLASS_NAME, 'cart-item')

            if not cart_items:
                print("-> Koszyk jest pusty, przerywam usuwanie.")
                break

            # Usuwamy ZAWSZE pierwszy element z listy
            delete_link = cart_items[0].find_element(By.CSS_SELECTOR, ".remove-from-cart")
            delete_link.click()

            # Czekamy chwilę aż Presta odświeży koszyk (ważne!)
            sleep(2)
            print(f"-> Usunięto produkt nr {i+1}")

        except Exception as e:
            print(f"-> Błąd przy usuwaniu: {e}")
            break


def process_of_buying_test(driver):
    print("KROK: Realizacja zamówienia (Checkout)...")
    # WAŻNE: Wracamy do koszyka po dodaniu adresu
    driver.get(f"{BASE_URL}/index.php?controller=cart")
    sleep(2)

    # --- FIX NA BŁĄD ElementClickIntercepted ---
    # Czekamy na przycisk checkout
    checkout_btn = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'a.btn.btn-primary')))

    # Używamy JavaScript do kliknięcia (omija zasłaniające elementy)
    driver.execute_script("arguments[0].click();", checkout_btn)
    sleep(3)

    # Debug: Sprawdzamy gdzie jesteśmy
    print(f"  -> Po kliknięciu checkout: URL={driver.current_url}, Title={driver.title}")

    # 1. Adres
    print("-> Potwierdzanie adresu...")
    # Czekamy na przycisk potwierdzenia adresu
    try:
        confirm_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'confirm-addresses')))
        print("  -> Używam istniejącego adresu z profilu")
        driver.execute_script("arguments[0].click();", confirm_btn)
    except:
        # Może być potrzeba wypełnienia nowego adresu
        print(f"  -> Nie znaleziono przycisku potwierdzenia adresu")
        print(f"  -> Obecny URL: {driver.current_url}")
        print(f"  -> Tytuł: {driver.title}")
        raise

    # 2. Dostawa (Wybór jednego z dwóch przewoźników)
    print("-> Wybór przewoźnika...")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, 'confirmDeliveryOption')))

    delivery_inputs = driver.find_elements(By.CSS_SELECTOR, ".delivery-option input")
    if len(delivery_inputs) >= 2:
        # Wybieramy drugiego (index 1)
        driver.execute_script("arguments[0].click();", delivery_inputs[1])
        print("-> Wybrano drugiego przewoźnika.")
    elif delivery_inputs:
        driver.execute_script("arguments[0].click();", delivery_inputs[0])
        print("-> Wybrano pierwszego przewoźnika (tylko jeden dostępny).")

    driver.find_element(By.NAME, 'confirmDeliveryOption').click()

    # 3. Płatność (Przy odbiorze)
    print("-> Wybór płatności...")
    sleep(2)

    # Próbujemy znaleźć dowolną opcję płatności
    payment_inputs = driver.find_elements(By.CSS_SELECTOR, ".payment-option input, input[name*='payment']")

    if payment_inputs:
        # Wybieramy pierwszą dostępną opcję
        driver.execute_script("arguments[0].click();", payment_inputs[0])
        print(f"-> Wybrano metodę płatności")
    else:
        # Próbujemy przez ID
        try:
            driver.find_element(By.ID, "payment-option-1").click()
            print("-> Wybrano payment-option-1")
        except:
            try:
                driver.find_element(By.ID, "payment-option-2").click()
                print("-> Wybrano payment-option-2")
            except:
                print("BŁĄD: Nie znaleziono żadnej opcji płatności")

    # 4. Zatwierdzenie
    driver.find_element(By.ID, "conditions_to_approve[terms-and-conditions]").click()
    driver.find_element(By.CSS_SELECTOR, '#payment-confirmation button').click()

    # Pobranie numeru zamówienia
    WebDriverWait(driver, 20).until(EC.title_contains('Order confirmation'))
    try:
        ref_text = driver.find_element(By.ID, "order-reference-value").text
        order_ref = ref_text.split(":")[-1].strip()
        print(f"-> Zamówienie złożone! Numer: {order_ref}")
        return order_ref
    except:
        return "UNKNOWN"


def check_status_and_invoice_test(driver):
    print("KROK: Sprawdzanie statusu i faktury...")
    driver.get(f"{BASE_URL}/index.php?controller=history")
    WebDriverWait(driver, 20).until(EC.title_contains('Order history'))

    try:
        # Pobieramy pierwszy wiersz (najnowsze zamówienie)
        row = driver.find_element(By.CSS_SELECTOR, "table tbody tr")
        status = row.find_element(By.CSS_SELECTOR, ".label-pill").text
        print(f"-> Status zamówienia: {status}")

        # Pobieranie faktury
        # Szukamy linku, który w href ma 'pdf' lub ikony PDF
        pdf_links = row.find_elements(By.CSS_SELECTOR, "a[href*='pdf']")
        if pdf_links:
            pdf_links[0].click()
            print("-> Kliknięto pobieranie faktury.")
            sleep(5) # Czekamy na pobranie
        else:
            print("-> Brak faktury do pobrania (może status zamówienia na to nie pozwala?).")

    except Exception as e:
        print(f"BŁĄD przy sprawdzaniu statusu: {e}")


def run_tests():
    driver = create_driver()
    driver.maximize_window()
    email = "student" + str(randint(10000, 99999)) + "@mail.pl"

    try:
        # 1. Dodawanie produktów (2 kategorie po 5 sztuk)
        # Zaktualizowane ID kategorii dla klastra:
        add_products_test(driver, f"{BASE_URL}/index.php?id_category=307&controller=category&id_lang=2", num_products=5)
        add_products_test(driver, f"{BASE_URL}/index.php?id_category=404&controller=category&id_lang=2", num_products=5)

        # 2. Wyszukiwanie (używamy ogólnej frazy, żeby losowanie miało sens)
        find_by_name_test(driver, "Wino")

        # 3. Usuwanie
        remove_from_cart_test(driver)

        # 4. Rejestracja
        registration_test(driver, email)

        # 4a. Dodanie adresu do profilu (WYMAGANE przed checkout)
        add_address_test(driver)

        # 5. Zakup
        process_of_buying_test(driver)

        # 6. Status i Faktura
        check_status_and_invoice_test(driver)

    except Exception as e:
        print(f"WYSTĄPIŁ BŁĄD KRYTYCZNY: {e}")
    finally:
        sleep(5)
        driver.quit()
        print("Test zakończony.")

if __name__ == "__main__":
    run_tests()
