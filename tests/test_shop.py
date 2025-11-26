import os
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from random import randint, choice
from time import sleep

# Ustawiamy jeden główny adres
BASE_URL = "http://127.0.0.1"

def create_driver():
    options = webdriver.FirefoxOptions()
    service = Service() 
    
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--ignore-ssl-errors")

    # --- KONFIGURACJA POBIERANIA PLIKÓW (DLA FAKTURY) ---
    # 0 = Pulpit, 1 = Domyślny systemowy, 2 = Wskazany folder
    options.set_preference("browser.download.folderList", 2)
    # Pobieraj do katalogu bieżącego (tam gdzie skrypt) lub ~/Downloads
    options.set_preference("browser.download.dir", os.getcwd())
    # Nie pytaj o zapisywanie plików PDF
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
    options.set_preference("pdfjs.disabled", True)  # Wyłącz wbudowaną przeglądarkę PDF

    driver = webdriver.Firefox(service=service, options=options)
    driver.set_window_size(1400, 900)
    driver.implicitly_wait(5)
    return driver


def registration_test(driver, email):
    driver.get(f"{BASE_URL}/login?create_account=1")
    WebDriverWait(driver, 10).until(EC.title_contains("Login"))

    driver.find_element(By.ID, "field-id_gender-1").click()
    driver.find_element(By.ID, "field-firstname").send_keys("Jan")
    driver.find_element(By.ID, "field-lastname").send_keys("Kowalski")
    driver.find_element(By.ID, "field-email").send_keys(email)
    driver.find_element(By.ID, "field-password").send_keys("Student123!")
    driver.find_element(By.ID, "field-birthday").send_keys("1995-05-31")

    # Checkboxy
    try:
        driver.find_element(By.NAME, "optin").click()
        driver.find_element(By.NAME, "customer_privacy").click()
        driver.find_element(By.NAME, "psgdpr").click()
    except:
        pass

    try:
        button = driver.find_element(By.CSS_SELECTOR, "button[data-link-action='save-customer']")
    except:
        button = driver.find_element(By.CSS_SELECTOR, ".btn.btn-primary.form-control-submit")
        
    button.click()
    WebDriverWait(driver, 20).until(lambda d: "login" not in d.current_url)
    print("KROK: Rejestracja zakończona sukcesem")


def add_products_test(driver, category_link, num_products):
    driver.get(category_link)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(
        (By.XPATH, '//*[contains(@class, "product-list")]')))

    products = driver.find_elements(
        By.XPATH, '//div[@id="js-product-list"]//a[@class="thumbnail product-thumbnail"]')
    product_links = [product.get_attribute("href") for product in products]

    added_counter = 0 

    for link in product_links:
        if added_counter >= num_products:
            break

        driver.get(link)
        
        try:
            add_btn_selector = (By.CSS_SELECTOR, '.btn.btn-primary.add-to-cart')
            WebDriverWait(driver, 1).until(EC.element_to_be_clickable(add_btn_selector))

            # --- WYMAGANIE: RÓŻNE ILOŚCI ---
            random_qty = randint(1, 2)
            
            quantity = driver.find_element(By.ID, 'quantity_wanted')
            quantity.send_keys(Keys.CONTROL + "a")
            quantity.send_keys(Keys.DELETE)
            quantity.send_keys(str(random_qty)) # Wpisujemy losową ilość
            
            driver.find_element(*add_btn_selector).click()
            
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
                (By.ID, "blockcart-modal")))
            
            print(f"-> Dodano produkt: {link} (Ilość: {random_qty})")
            added_counter += 1 

        except TimeoutException:
            print(f"-> Pominięto (niedostępny): {link}")
            continue 
            
    print(f"KROK: Dodano {added_counter} produktów z kategorii.")


def find_by_name_test(driver, name_of_product):
    driver.get(BASE_URL)
    search_bar = driver.find_element(By.CLASS_NAME, 'ui-autocomplete-input')
    search_bar.click()
    search_bar.send_keys(name_of_product)
    search_bar.send_keys(Keys.ENTER)

    WebDriverWait(driver, 20).until(EC.title_contains('Search'))

    products = driver.find_elements(
        By.XPATH, '//div[@id="js-product-list"]//a[@class="thumbnail product-thumbnail"]')
    
    if products:
        random_link = choice(products).get_attribute("href")
        driver.get(random_link)
        
        add_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, '.btn.btn-primary.add-to-cart')))
        add_btn.click()
        
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
                (By.ID, "blockcart-modal")))
        print(f"KROK: Znaleziono '{name_of_product}' i dodano losowy wynik.")
    else:
        print(f"BŁĄD: Nie znaleziono produktu '{name_of_product}'")


def remove_from_cart_test(driver):
    driver.get(f"{BASE_URL}/cart?action=show")
    WebDriverWait(driver, 20).until(EC.title_contains('Cart'))

    # --- WYMAGANIE: USUNIĘCIE 3 PRODUKTÓW ---
    print("KROK: Usuwanie 3 produktów z koszyka...")
    
    for i in range(3):
        try:
            # Odświeżamy listę elementów za każdym razem, bo DOM się zmienia po usunięciu
            cart_items = driver.find_elements(By.CLASS_NAME, 'cart-item')
            if not cart_items:
                print("Koszyk jest już pusty!")
                break
            
            # Szukamy przycisku usuwania w pierwszym elemencie
            remove_btn = cart_items[0].find_element(By.CLASS_NAME, "remove-from-cart")
            remove_btn.click()
            
            # Czekamy aż element zniknie (staleness) lub lista się zmniejszy
            sleep(2) # Krótki sleep jest tu najbezpieczniejszy dla stabilności przy AJAX Presty
            print(f"-> Usunięto produkt nr {i+1}")
            
        except Exception as e:
            print(f"Problem przy usuwaniu: {e}")
            break


def process_of_buying_test(driver):
    driver.get(f"{BASE_URL}/cart?action=show")
    WebDriverWait(driver, 20).until(EC.title_contains('Cart'))
    driver.find_element(By.CSS_SELECTOR, 'a.btn.btn-primary').click()

    # Adres
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "field-address1")))
    driver.find_element(By.ID, "field-address1").send_keys("ul. Testowa 5")
    driver.find_element(By.ID, "field-postcode").send_keys("80-180")
    driver.find_element(By.ID, "field-city").send_keys("Gdańsk")
    driver.find_element(By.NAME, 'confirm-addresses').click()

    # --- WYMAGANIE: Wybór jednego z dwóch przewoźników ---
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, 'confirmDeliveryOption')))
    delivery_options = driver.find_elements(By.CSS_SELECTOR, ".delivery-option input")
    # Wybieramy drugi jeśli jest, jeśli nie to pierwszy
    if len(delivery_options) >= 2:
        driver.execute_script("arguments[0].click();", delivery_options[1])
        print("-> Wybrano drugiego przewoźnika")
    elif delivery_options:
        driver.execute_script("arguments[0].click();", delivery_options[0])
        print("-> Wybrano pierwszego przewoźnika (tylko jeden dostępny)")
        
    driver.find_element(By.NAME, 'confirmDeliveryOption').click()

    # --- WYMAGANIE: Płatność przy odbiorze ---
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "payment-option-2")))
    
    # Szukamy opcji "Cash on delivery" lub "Przy odbiorze"
    payment_options = driver.find_elements(By.CSS_SELECTOR, ".payment-option label")
    cod_found = False
    
    for index, option in enumerate(payment_options):
        text = option.text.lower()
        if "cash" in text or "odbiorze" in text or "delivery" in text:
            # Klikamy odpowiedni input (id payment-option-X)
            input_id = option.find_element(By.XPATH, "./preceding-sibling::span/input").get_attribute("id")
            driver.find_element(By.ID, input_id).click()
            print(f"-> Wybrano płatność: {option.text}")
            cod_found = True
            break
            
    if not cod_found:
        print("UWAGA: Nie znaleziono 'Płatności przy odbiorze'. Wybieram domyślną.")
        driver.find_element(By.ID, "payment-option-2").click() # Fallback

    # Warunki i Zamówienie
    driver.find_element(By.ID, "conditions_to_approve[terms-and-conditions]").click()
    driver.find_element(By.CSS_SELECTOR, '#payment-confirmation button').click()

    WebDriverWait(driver, 20).until(EC.title_contains('Order'))
    
    try:
        ref_element = driver.find_element(By.ID, "order-reference-value")
        order_ref = ref_element.text.split(":")[-1].strip()
        print(f"KROK: Zamówienie złożone. Numer: {order_ref}")
        return order_ref
    except:
        return "ERROR"


def check_status_and_invoice_test(driver):
    driver.get(f"{BASE_URL}/order-history")
    WebDriverWait(driver, 20).until(EC.title_contains('Order history'))
    print("KROK: Sprawdzanie statusu zamówienia...")
    
    # Pobieramy pierwszy wiersz (ostatnie zamówienie)
    try:
        first_row = driver.find_element(By.CSS_SELECTOR, "table tbody tr")
        status = first_row.find_element(By.CSS_SELECTOR, ".label-pill").text
        print(f"-> Status zamówienia: {status}")
        
        # --- WYMAGANIE: Pobranie faktury VAT ---
        print("KROK: Pobieranie faktury VAT...")
        # Szukamy linku do PDF (zwykle ikonka file-pdf-o lub tekst Invoice)
        # Selektor może się różnić zależnie od szablonu, szukamy po hrefie zawierającym 'pdf'
        pdf_link = first_row.find_element(By.CSS_SELECTOR, "a[href*='pdf']")
        pdf_link.click()
        print("-> Kliknięto pobieranie faktury (sprawdź folder ze skryptem lub Pobrane)")
        sleep(5) # Czekamy chwilę aż się pobierze
        
    except NoSuchElementException:
        print("BŁĄD: Nie znaleziono zamówienia lub linku do faktury w historii.")
    except Exception as e:
        print(f"BŁĄD przy fakturze: {e}")


def run_tests():
    driver = create_driver()
    driver.maximize_window()
    email = "student" + str(randint(10000, 99999)) + "@mail.pl"
    
    try:
        # 1. Dodanie 10 produktów (5 z jednej, 5 z drugiej kat.)
        # UWAGA: Upewnij się, że ID kategorii (307, 403) są poprawne dla Twojego sklepu
        add_products_test(driver, f"{BASE_URL}/en/307-wina", num_products=5)
        add_products_test(driver, f"{BASE_URL}/en/404-delikatesy", num_products=5)
        
        # 2. Wyszukanie i dodanie losowego
        find_by_name_test(driver, "Zestaw prezentowy Armagnac Haut Marin XO zapakowany")
        
        # 3. Usunięcie 3 produktów
        remove_from_cart_test(driver)
        
        # 4. Rejestracja
        registration_test(driver, email)
        
        # 5, 6, 7, 8. Zamówienie, Płatność, Przewoźnik, Zatwierdzenie
        process_of_buying_test(driver)
        
        # 9, 10. Status i Faktura
        check_status_and_invoice_test(driver)

    except Exception as e:
        print(f"WYSTĄPIŁ BŁĄD KRYTYCZNY: {e}")
    finally:
        # driver.quit() # Zakomentowane, żebyś widział efekt końcowy
        print("Test zakończony.")

if __name__ == "__main__":
    run_tests()