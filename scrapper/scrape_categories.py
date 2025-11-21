import requests
from bs4 import BeautifulSoup
import csv

URL = "https://dobrewina.pl/"
OUTPUT_FILE = "./data/import_categories.csv"

def get_soup(url):
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    except Exception as e:
        print(f"Błąd pobierania {url}: {e}")
        return None

def scrape_categories():
    soup = get_soup(URL)
    if not soup:
        return

    menu = soup.find(id="top-menu")
    if not menu:
        menu = soup.find(class_="top-menu")
    
    if not menu:
        print("Nie znaleziono menu głównego. Sprawdź selektory CSS.")
        return

    categories_data = []
    
    current_id = 100

    main_categories = menu.find_all("li", recursive=False)

    for main_cat in main_categories:
        link = main_cat.find("a")
        if not link: continue
        
        main_name = link.get_text(strip=True)
        print(f"Znaleziono główną: {main_name}")

        categories_data.append({
            "ID": current_id,
            "Active (0/1)": 1,
            "Name": main_name,
            "Parent category": "Strona główna", 
            "Root category (0/1)": 0,
            "Description": f"Kategoria {main_name} pobrana automatycznie."
        })
        parent_name = main_name
        current_id += 1

        submenu = main_cat.find("ul") 
        if submenu:
            sub_links = submenu.find_all("a") 
            for sub_link in sub_links:
                sub_name = sub_link.get_text(strip=True)
                print(f"  -> Podkategoria: {sub_name}")
                
                categories_data.append({
                    "ID": current_id,
                    "Active (0/1)": 1,
                    "Name": sub_name,
                    "Parent category": parent_name,
                    "Root category (0/1)": 0,
                    "Description": f"Podkategoria {sub_name}."
                })
                current_id += 1

    with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=categories_data[0].keys(), delimiter=';')
        writer.writeheader()
        writer.writerows(categories_data)

    print(f"\nSukces! Dane zapisano do {OUTPUT_FILE}")

if __name__ == "__main__":
    scrape_categories()