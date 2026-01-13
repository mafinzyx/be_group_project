from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from time import sleep

BASE_URL = "http://localhost:8080"

# Простой тест для проверки корзины
driver = webdriver.Firefox()
driver.set_window_size(1400, 900)
driver.implicitly_wait(5)

try:
    print("1. Открываем главную страницу...")
    driver.get(BASE_URL)
    sleep(2)

    print("2. Переходим к продукту...")
    driver.get(f"{BASE_URL}/index.php?id_product=816&controller=product&id_lang=2")
    sleep(2)

    print("3. Добавляем в корзину...")
    add_btn = driver.find_element(By.CSS_SELECTOR, '.btn.btn-primary.add-to-cart')
    add_btn.click()

    print("4. Ждем модальное окно...")
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "blockcart-modal")))
    print("  -> Модальное окно появилось!")

    # Проверяем количество в header
    try:
        cart_count = driver.find_element(By.CSS_SELECTOR, ".cart-products-count").text
        print(f"  -> Количество в header: {cart_count}")
    except:
        print("  -> Не удалось найти счетчик в header")

    print("5. Закрываем модальное окно...")
    try:
        close_btn = driver.find_element(By.CSS_SELECTOR, "#blockcart-modal .close")
        close_btn.click()
        sleep(1)
    except:
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
        sleep(1)

    print("6. Переходим на страницу корзины...")
    driver.get(f"{BASE_URL}/index.php?controller=cart")
    sleep(3)

    print(f"  -> URL: {driver.current_url}")
    print(f"  -> Title: {driver.title}")

    # Проверяем наличие товаров
    cart_items = driver.find_elements(By.CLASS_NAME, 'cart-item')
    print(f"  -> Товаров в корзине: {len(cart_items)}")

    if len(cart_items) > 0:
        print("✅ ТОВАР СОХРАНЕН В КОРЗИНЕ!")
    else:
        print("❌ КОРЗИНА ПУСТА!")

        # Дополнительная проверка - есть ли сообщение о пустой корзине
        try:
            empty_msg = driver.find_element(By.CSS_SELECTOR, ".cart-empty, .alert")
            print(f"  -> Сообщение: {empty_msg.text[:100]}")
        except:
            pass

except Exception as e:
    print(f"ОШИБКА: {e}")
finally:
    sleep(5)
    driver.quit()
