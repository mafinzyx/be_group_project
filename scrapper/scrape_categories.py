import requests
from bs4 import BeautifulSoup
import csv
import json
from urllib.parse import urljoin

# config
URL_BASE = "https://dobrewina.pl/"
OUTPUT_FILE_CATEGORIES = "./data/import_categories.csv"
OUTPUT_FILE_PRODUCTS = "./data/products.csv"

# kategorie naglowki
CATEGORY_FIELDNAMES = ["ID", "Active (0/1)", "Name", "URL", "Parent category", "Root category (0/1)", "Description"]

# produkty naglowki
PRODUCT_FIELDNAMES = [
    "Product ID", "Name", "Category", "Description", "Price",
    "Image 1 URL (Hi-Res)", "Image 2 URL (Hi-Res)",
    "Country", "Region", "Grape Varieties (Szczepy)", "Winetype (Rodzaj)",
    "Dryness (Wytrawność)", "Alcohol %", "Pairing (Polecane do)", "Product URL"
]


def get_soup(url):
    """Pobiera i parsuje stronę."""
    try:
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'},
                                timeout=15)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    except Exception as e:
        print(f"Błąd pobierania {url}: {e}")
        return None


def resolve_url(relative_url, base_url=URL_BASE):
    """Konwertuje względny URL na bezwzględny."""
    if not relative_url:
        return 'N/A'
    return urljoin(base_url, relative_url)


def scrape_categories():
    """Scrapuje menu główne i podmenu do 3 poziomów głębokości."""
    soup = get_soup(URL_BASE)
    if not soup:
        return []

    menu = soup.find(id="top-menu")
    if not menu:
        print("Nie znaleziono menu głównego #top-menu.")
        return []

    categories_data = []
    current_id = 100

    main_categories = menu.find_all("li", recursive=False)

    for main_cat in main_categories:
        link_level_0 = main_cat.find("a", attrs={"data-depth": "0"})
        if not link_level_0: continue

        name_level_0 = link_level_0.get_text(strip=True)
        url_level_0 = link_level_0.get('href')

        categories_data.append({
            "ID": current_id, "Active (0/1)": 1, "Name": name_level_0, "URL": url_level_0,
            "Parent category": "Strona główna", "Root category (0/1)": 1,
            "Description": f"Kategoria główna: {name_level_0}."
        })
        parent_name_level_0 = name_level_0
        current_id += 1

        submenu_level_1 = main_cat.find("ul", attrs={"data-depth": "1"})

        if submenu_level_1:
            items_level_1 = submenu_level_1.find_all("li", recursive=False)

            for item_level_1 in items_level_1:
                link_level_1 = item_level_1.find("a", attrs={"data-depth": "1"})
                if not link_level_1: continue

                name_level_1 = link_level_1.get_text(strip=True)
                url_level_1 = link_level_1.get('href')

                categories_data.append({
                    "ID": current_id, "Active (0/1)": 1, "Name": name_level_1, "URL": url_level_1,
                    "Parent category": parent_name_level_0, "Root category (0/1)": 0,
                    "Description": f"Podkategoria poziomu 1: {name_level_1}."
                })
                parent_name_level_1 = name_level_1
                current_id += 1

                submenu_level_2 = item_level_1.find("ul", attrs={"data-depth": "2"})

                if submenu_level_2:
                    items_level_2 = submenu_level_2.find_all("li", recursive=False)

                    for item_level_2 in items_level_2:
                        link_level_2 = item_level_2.find("a", attrs={"data-depth": "2"})
                        if not link_level_2: continue

                        name_level_2 = link_level_2.get_text(strip=True)
                        url_level_2 = link_level_2.get('href')

                        categories_data.append({
                            "ID": current_id, "Active (0/1)": 1, "Name": name_level_2, "URL": url_level_2,
                            "Parent category": parent_name_level_1, "Root category (0/1)": 0,
                            "Description": f"Podkategoria poziomu 2: {name_level_2}."
                        })
                        parent_name_level_2 = name_level_2
                        current_id += 1

                        submenu_level_3 = item_level_2.find("ul", attrs={"data-depth": "3"})

                        if submenu_level_3:
                            items_level_3 = submenu_level_3.find_all("li", recursive=False)

                            for item_level_3 in items_level_3:
                                link_level_3 = item_level_3.find("a", attrs={"data-depth": "3"})
                                if not link_level_3: continue

                                name_level_3 = link_level_3.get_text(strip=True)
                                url_level_3 = link_level_3.get('href')

                                categories_data.append({
                                    "ID": current_id, "Active (0/1)": 1, "Name": name_level_3, "URL": url_level_3,
                                    "Parent category": parent_name_level_2, "Root category (0/1)": 0,
                                    "Description": f"Podkategoria poziomu 3: {name_level_3}."
                                })
                                current_id += 1

    with open(OUTPUT_FILE_CATEGORIES, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=CATEGORY_FIELDNAMES, delimiter=';')
        writer.writeheader()
        writer.writerows(categories_data)

    print(f"\nSukces! Dane kategorii zapisano do {OUTPUT_FILE_CATEGORIES}")
    return categories_data


def scrape_single_product_details(product_url):
    """Pobiera detale produktu."""
    product_soup = get_soup(product_url)
    if not product_soup:
        return None

    data = {}

    for field in PRODUCT_FIELDNAMES:
        data[field] = "N/A"

    data["Product URL"] = product_url
    data["Product ID"] = product_url.split('-')[-1].split('.')[0]

    # 1. NAZWA PRODUKTU
    name_tag = product_soup.find('h1')
    data['Name'] = name_tag.get_text(strip=True) if name_tag else data['Name']

    # 2. CENA
    discount_price_tag = product_soup.find('span', class_='discount-price-display')

    if discount_price_tag:
        data['Price'] = discount_price_tag.get_text(strip=True).replace('\xa0', ' ')
    else:
        regular_price_tag = product_soup.find('span', class_='current-price-display')
        if regular_price_tag:
            data['Price'] = regular_price_tag.get_text(strip=True).replace('\xa0', ' ')

    # 3. OPIS PRODUKTU
    description_short_tag = product_soup.find(id='product-description-short')
    description_full_tag = product_soup.find('div', class_='product-description')

    if description_short_tag:
        data['Description'] = description_short_tag.get_text(strip=True)

    if data['Description'] in ("N/A", "") and description_full_tag:
        full_text = description_full_tag.get_text(separator=' ', strip=True)
        data['Description'] = full_text if full_text else "N/A"

    # 4. ZDJĘCIA W WYSOKIEJ ROZDZIELCZOŚCI
    hi_res_urls = []
    modal_images_container = product_soup.find('div', id='js-product-images-slider')

    if modal_images_container:
        for img_tag in modal_images_container.find_all('img', attrs={'data-src': True}):
            img_url = img_tag.get('data-src')
            resolved_url = resolve_url(img_url)
            if resolved_url != 'N/A' and resolved_url not in hi_res_urls:
                hi_res_urls.append(resolved_url)

    if len(hi_res_urls) >= 1:
        data['Image 1 URL (Hi-Res)'] = hi_res_urls[0]
    if len(hi_res_urls) >= 2:
        data['Image 2 URL (Hi-Res)'] = hi_res_urls[1]

    # 5. I 6. ATRYBUTY (Szczepy, Danie, itp.)
    details_section = product_soup.find('div', class_='product-details')

    if details_section:
        for item in details_section.find_all('div', class_='product-details__item'):
            name_tag = item.find('div', class_='product-details__name')
            value_tag = item.find('div', class_='product-details__value')

            if name_tag and value_tag:
                key = name_tag.get_text(strip=True).replace(':', '')
                value_text = value_tag.get_text(strip=True)

                # Danie (Pairing)
                if key == 'Danie':
                    pairing_list = [img.get('title') for img in value_tag.find_all('img') if img.get('title')]
                    data['Pairing (Polecane do)'] = ", ".join(pairing_list) if pairing_list else data[
                        'Pairing (Polecane do)']

                # Mapowanie pozostałych kluczy
                elif value_text and value_text != 'N/A':
                    if key == 'Kraj':
                        data['Country'] = value_text
                    elif key == 'Region':
                        data['Region'] = value_text

                    # Szczepy
                    elif key in ['Szczep', 'Szczepy']:
                        grape_names = [t.strip() for t in value_tag.stripped_strings if t.strip()]
                        data['Grape Varieties (Szczepy)'] = ", ".join(grape_names)

                    elif key == 'Rodzaj':
                        data['Winetype (Rodzaj)'] = value_text
                    elif key == 'Wytrawność':
                        data['Dryness (Wytrawność)'] = value_text
                    elif key == 'Zawartość alkoholu':
                        data['Alcohol %'] = value_text

    return data


# --- TEST ---
# TODO: SZCZEPOW nie pobiera prawidlowo- jest N/A dla testow mozna sprawdzic ten link co jest w main
def test_single_product(product_url):
    """Pobiera i wyświetla dane dla jednego produktu w celu szybkiego testu."""
    print(f"--- ROZPOCZĘCIE TESTU DLA: {product_url} ---")

    product_details = scrape_single_product_details(product_url)

    if product_details:
        print("\n Sukces! Pobrane detale produktu:")
        print(json.dumps(product_details, indent=4, ensure_ascii=False))

        if product_details['Name'] == 'N/A' or product_details['Price'] == 'N/A':
            print("\n OSTRZEŻENIE: Kluczowe pola (Nazwa/Cena) są puste. Sprawdź selektory.")

        if product_details['Image 1 URL (Hi-Res)'] == 'N/A':
            print("OSTRZEŻENIE: Nie udało się pobrać adresu URL głównego zdjęcia.")

    else:
        print("\n BŁĄD: Nie udało się pobrać strony produktu.")


def scrape_products_by_category(category_name, category_url):
    """Iteruje przez strony w ramach jednej kategorii, zbiera linki do produktów i pobiera detale."""
    all_product_details = []
    current_page_url = category_url
    processed_pages = set()

    while current_page_url:
        if current_page_url in processed_pages:
            print(f" -> Pomijanie już przetworzonej strony: {current_page_url}")
            break

        print(f" -> Przetwarzanie strony: {current_page_url}")
        page_soup = get_soup(current_page_url)
        processed_pages.add(current_page_url)

        if not page_soup:
            break

        product_link_elements = page_soup.find_all('a', class_='product-title')
        product_urls = [link.get('href') for link in product_link_elements if link.get('href')]

        print(f" -> Znaleziono {len(product_urls)} produktów na stronie. Rozpoczynanie pobierania detali.")

        for product_url in product_urls:
            product_details = scrape_single_product_details(product_url)
            if product_details:
                product_details["Category"] = category_name
                all_product_details.append(product_details)
                log_name = product_details['Name'] if product_details['Name'] and product_details[
                    'Name'] != 'N/A' else 'Brak nazwy/N/A'
                print(f" -> Zapisano: {log_name}")

        pagination_next = page_soup.find('a', class_='js-search-link', rel='next')

        if pagination_next and pagination_next.get('href'):
            current_page_url = pagination_next.get('href')
        else:
            current_page_url = None

    return all_product_details


def run_scraper():
    """Główny punkt wejścia do skryptu."""
    print("Rozpoczęcie scrapowania...")
    categories_data = scrape_categories()

    if not categories_data:
        print("Nie udało się pobrać kategorii. Zakończenie.")
        return

    # Logika dla kategorii liści
    parent_names = {c['Parent category'] for c in categories_data if c['Parent category'] != 'Strona główna'}
    leaf_categories = [cat for cat in categories_data if
                       cat['Name'] not in parent_names and cat['Root category (0/1)'] == 0]

    print(
        f"Znaleziono {len(categories_data)} kategorii. Zredukowano do {len(leaf_categories)} unikalnych kategorii 'liści' do scrapowania produktów.")

    all_products = []
    processed_urls = set()

    for category in leaf_categories:
        category_url = category.get("URL")
        category_name = category.get("Name")

        if category_url in processed_urls or '/content/' in category_url:
            continue

        processed_urls.add(category_url)

        print(f"\n--- Rozpoczęcie pobierania produktów dla kategorii LIŚCIA: {category_name} ({category_url}) ---")
        products = scrape_products_by_category(category_name, category_url)
        all_products.extend(products)

    if all_products:
        unique_products_map = {p["Product ID"]: p for p in all_products}
        final_products = list(unique_products_map.values())

        print(f"\nZebrano łącznie {len(final_products)} unikalnych rekordów produktów.")

        with open(OUTPUT_FILE_PRODUCTS, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=PRODUCT_FIELDNAMES, delimiter=';', extrasaction='ignore')
            writer.writeheader()
            writer.writerows(final_products)

        print(f"\n Scraping zakończony pomyślnie! Dane produktów zapisano do {OUTPUT_FILE_PRODUCTS}")
    else:
        print("\nNie znaleziono żadnych produktów do zapisania.")


if __name__ == "__main__":
    TEST_URL = "https://dobrewina.pl/wino-biale/361-wino-biale-la-marina-cuvee-oceane-igp-francuskie-wytrawne-075-l-3760094286557.html"

    test_single_product(TEST_URL)
    # run_scraper()