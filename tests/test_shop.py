from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from random import randint, choice
from time import sleep

# settings for linux


def create_driver():
    options = webdriver.FirefoxOptions()
    options.add_argument("--width=1400")
    options.add_argument("--height=900")
    service = Service("/snap/bin/geckodriver")
    # ignore certificate errors
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--ignore-ssl-errors")  # ignore ssl errors
    options.add_argument(
        '--disable-web-security')  # disable web security
    driver = webdriver.Firefox(service=service, options=options)
    driver.implicitly_wait(5)
    return driver


def registration_test(driver, email):
    driver.get("http://localhost/login?create_account=1")
    WebDriverWait(driver, 120).until(EC.title_is("Login"))

    gender_mr = driver.find_element(By.ID, "field-id_gender-1")
    gender_mr.click()

    first_name = driver.find_element(By.ID, "field-firstname")
    first_name.send_keys("John")

    last_name = driver.find_element(By.ID, "field-lastname")
    last_name.send_keys("Pork")

    email_name = driver.find_element(By.ID, "field-email")
    email_name.send_keys(email)

    password = driver.find_element(By.ID, "field-password")
    password.send_keys("StrongPass123")

    birthday = driver.find_element(By.ID, "field-birthday")
    birthday.send_keys("1970-05-31")

    # first checkbox
    newsletter = driver.find_element(By.NAME, "optin")
    newsletter.click()

    # second checkbox
    privacy_policy = driver.find_element(By.NAME, "customer_privacy")
    privacy_policy.click()

    # third checkbox
    psgdpr = driver.find_element(By.NAME, "psgdpr")
    psgdpr.click()

    button = driver.find_element(
        By.CSS_SELECTOR, ".btn.btn-primary.form-control-submit.float-xs-right")
    button.click()

    WebDriverWait(driver, 120).until(EC.title_is("dobrewina"))
    print("TEST 4!  Registration successful")


def add_products_test(driver, category_link, num_products=5):
    driver.get(category_link)
    WebDriverWait(driver, 120).until(EC.presence_of_element_located(
        (By.XPATH, '//*[contains(@class, "product-list")]')))

    products = driver.find_elements(
        By.XPATH, '//div[@id="js-product-list"]//a[@class="thumbnail product-thumbnail"]')
    product_links = [product.get_attribute("href") for product in products]

    for link in product_links[:num_products]:
        driver.get(link)
        WebDriverWait(driver, 120).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '.btn.btn-primary.add-to-cart')))

        quantity = driver.find_element(By.ID, 'quantity_wanted')
        # to delete existing number in this fieild
        quantity.send_keys(Keys.CONTROL + "a")
        quantity.send_keys(Keys.DELETE)
        # quantity.send_keys(randint(1, 7))
        quantity.send_keys(1)
        
        add_to_cart = driver.find_element(
            By.CSS_SELECTOR, '.btn.btn-primary.add-to-cart')
        add_to_cart.click()
        # waiting for "Produkt dodany poprawnie do Twojego koszyka" window to appear
        WebDriverWait(driver, 120).until(EC.presence_of_element_located(
            (By.CLASS_NAME, "modal-backdrop.fade.in")))
    print("TEST 1!  Products added to cart from category: ", category_link)


def find_by_name_test(driver, name_of_product):
    driver.get("http://localhost")
    search_bar = driver.find_element(By.CLASS_NAME, 'ui-autocomplete-input')
    search_bar.click()
    search_bar.send_keys(name_of_product)
    search_bar.send_keys(Keys.ENTER)

    WebDriverWait(driver, 120).until(EC.title_is('Search'))

    products = driver.find_elements(
        By.XPATH, '//div[@id="js-product-list"]//a[@class="thumbnail product-thumbnail"]')
    product_links = [product.get_attribute("href") for product in products]
    random_link = choice(product_links)

    driver.get(random_link)
    WebDriverWait(driver, 120).until(EC.title_contains(name_of_product[:-1]))

    add_to_cart = driver.find_element(
        By.CSS_SELECTOR, '.btn.btn-primary.add-to-cart')
    add_to_cart.click()
    # waiting for "Produkt dodany poprawnie do Twojego koszyka" window to appear
    WebDriverWait(driver, 120).until(EC.presence_of_element_located(
        (By.CLASS_NAME, "modal-backdrop.fade.in")))
    print("TEST 2!  Product added to cart: ", name_of_product)


def remove_from_cart_test(driver):
    driver.get("http://localhost/cart?action=show")
    WebDriverWait(driver, 120).until(EC.title_is('Cart'))

    for _ in range(3):
        cart_items = driver.find_elements(By.CLASS_NAME, 'cart-item')
        if not cart_items:
            print("Cart is empty")
            break

        remove_button = cart_items[0].find_element(
            By.CSS_SELECTOR, "i.material-icons.float-xs-left")
        remove_button.click()

        WebDriverWait(driver, 120).until(EC.staleness_of(cart_items[0]))
    print("TEST 3!  Products removed from cart")


def process_of_buying_test(driver):
    driver.get("http://localhost/cart?action=show")
    WebDriverWait(driver, 120).until(EC.title_is('Cart'))

    checkout_button = driver.find_element(By.CSS_SELECTOR, 'a.btn.btn-primary')
    checkout_button.click()

    address = driver.find_element(By.ID, "field-address1")
    address.send_keys("ul. Kosmonawtow 12")

    post_code = driver.find_element(By.ID, "field-postcode")
    post_code.send_keys("12-228")

    city = driver.find_element(By.ID, "field-city")
    city.send_keys("Grodno")

    next_button = driver.find_element(By.NAME, 'confirm-addresses')
    next_button.click()

    delivery_button = driver.find_element(By.ID, "delivery_option[8]")
    delivery_button.click()

    next_button = driver.find_element(By.NAME, 'confirmDeliveryOption')
    next_button.click()

    payment_button = driver.find_element(By.ID, "payment-option-2")
    payment_button.click()

    conditions = driver.find_element(
        By.ID, "conditions_to_approve[terms-and-conditions]")
    conditions.click()

    order_button = driver.find_element(
        By.CSS_SELECTOR, 'button.btn.btn-primary.center-block')
    order_button.click()

    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, 'number-input')))
    card_number = driver.find_element(By.ID, "number-input")
    card_number.send_keys("4444333322221111")

    date_number = driver.find_element(By.ID, "date-input")
    date_number.send_keys("1229")

    cvv_number = driver.find_element(By.ID, "cvv-input")
    cvv_number.send_keys("123")

    submit_button = driver.find_element(
        By.CSS_SELECTOR, "input[name='submit']")
    submit_button.click()

    WebDriverWait(driver, 120).until(EC.title_is('Order confirmation'))
    order_reference = driver.find_element(By.ID, "order-reference-value")
    order_text = order_reference.text
    order_number = order_text.split(":")[-1].strip()

    print("TEST 5!  Order number: ", order_number)
    return order_number


def order_tracking_test(driver, tracking_number):
    order_history = driver.find_element(By.XPATH, '//*[@id="footer_account_list"]/li[2]/a')
    order_history.click()
    WebDriverWait(driver, 120).until(EC.title_is('Order history'))

    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
    for row in rows:
        if tracking_number in row.text:
            fax_button = row.find_element(
                By.CSS_SELECTOR, "td.text-sm-center.hidden-md-down a i.material-icons")
            fax_button.click()
            sleep(5)
            button = row.find_element(
                By.CSS_SELECTOR, "a[data-link-action='view-order-details']")
            button.click()

    WebDriverWait(driver, 120).until(EC.title_is('dobrewina'))
    print("TEST 6!  Order tracking successful")


def run_tests():
    driver = create_driver()
    driver.maximize_window()
    email = "test" + str(randint(1000, 9999)) + "@gmail.com"
    try:
        category_link1 = "http://localhost/en/39-wina"
        add_products_test(driver, category_link1, num_products=5)
        category_link2 = "http://localhost/en/136-delikatesy"
        add_products_test(driver, category_link2, num_products=5)
        name_of_product = "Zestaw"
        find_by_name_test(driver, name_of_product)
        remove_from_cart_test(driver)
        registration_test(driver, email)
        tracking_number = process_of_buying_test(driver)
        order_tracking_test(driver, tracking_number)

    finally:
        driver.quit()


run_tests()
