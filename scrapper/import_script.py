import csv
import requests
import xml.etree.ElementTree as ET
import os
import re
from io import BytesIO

# --- IMPORTUJEMY KLASĘ Z DRUGIEGO PLIKU ---
try:
    from update_stock_and_images import PrestaUpdater
except ImportError:
    print("UWAGA: Nie znaleziono pliku update_stock_and_images.py w tym samym katalogu!")
    PrestaUpdater = None

# --- KONFIGURACJA ---
API_URL = "http://127.0.0.1/api"
API_KEY = "R7FM7TCGA6NJRJU49MFTSJDP2JQ481U1"

FILE_CATEGORIES = "./data/import_categories.csv"
FILE_PRODUCTS = "./data/products.csv"

FEATURE_MAPPING = {
    "Country": "Kraj",
    "Region": "Region",
    "Grape Varieties (Szczepy)": "Szczep",
    "Winetype (Rodzaj)": "Rodzaj",
    "Dryness (Wytrawność)": "Wytrawność",
    "Alcohol %": "Zawartość alkoholu",
    "Pairing (Polecane do)": "Danie"
}


class PrestaShopImporter:
    def __init__(self, api_url, api_key):
        self.api_url = api_url.rstrip('/')
        self.session = requests.Session()
        self.session.auth = (api_key, '')
        self.category_map = {}
        self.feature_map = {}
        self.feature_value_map = {}

    def _slugify(self, text):
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s-]', '', text)
        return re.sub(r'[\s-]+', '-', text).strip('-')

    def _clean_price(self, price_str):
        if not price_str or price_str == 'N/A':
            return "0.00"
        return price_str.replace(' zł', '').replace(' ', '').replace('\xa0', '').replace(',', '.')

    def _add_child(self, parent, tag, text=None):
        """Inteligentne dodawanie pól (rozróżnia pola zwykłe od językowych)."""
        elem = parent.find(tag)

        is_multilang = False
        if elem is not None:
            if elem.find('language') is not None:
                is_multilang = True
        else:

            elem = ET.SubElement(parent, tag)

        if text is not None:
            if is_multilang:

                for child in list(elem):
                    elem.remove(child)

                lang1 = ET.SubElement(elem, 'language', id='1')
                lang1.text = str(text)

                lang2 = ET.SubElement(elem, 'language', id='2')
                lang2.text = str(text)
            else:

                elem.text = str(text)

    def _get_blank_schema(self, resource):
        if resource == 'categories':
            xml_str = """<prestashop><category>
                <id_parent/><active/><name><language id="1"/></name>
                <link_rewrite><language id="1"/></link_rewrite>
                <description><language id="1"/></description>
            </category></prestashop>"""
        elif resource == 'products':
            xml_str = """<prestashop><product>
                <price/><name><language id="1"/></name>
                <description><language id="1"/></description>
                <id_category_default/><id_tax_rules_group/>
                <type/><id_shop_default/><minimal_quantity/>
                <available_for_order/><link_rewrite><language id="1"/></link_rewrite>
                <active/><state/><indexed/><show_price/><reference/>
                <associations><categories/><product_features/></associations>
            </product></prestashop>"""
        elif resource == 'product_features':
            xml_str = """<prestashop><product_feature>
                <name><language id="1"/></name>
            </product_feature></prestashop>"""
        elif resource == 'product_feature_values':
            xml_str = """<prestashop><product_feature_value>
                <id_feature/><value><language id="1"/></value><custom/>
            </product_feature_value></prestashop>"""
        elif resource == 'images':
            return None
        else:
            try:
                url = f"{self.api_url}/{resource}?schema=blank"
                response = self.session.get(url)
                if response.status_code == 200 and b'<errors>' not in response.content:
                    return ET.fromstring(response.content)
            except:
                pass
            return ET.fromstring(f"<prestashop><{resource[:-1]}/></prestashop>")
        return ET.fromstring(xml_str)

    def post_resource(self, resource, xml_data):
        url = f"{self.api_url}/{resource}"
        xml_str = ET.tostring(xml_data, encoding='utf-8')
        try:
            response = self.session.post(url, data=xml_str)
            if response.status_code in (200, 201):
                root = ET.fromstring(response.content)
                tag_map = {'categories': 'category', 'products': 'product', 'product_features': 'product_feature',
                           'product_feature_values': 'product_feature_value'}
                search_tag = tag_map.get(resource, resource)
                node = root.find(search_tag)
                if node is not None: return node.find('id').text
                return None
            else:
                return None
        except Exception as e:
            print(f"[WYJĄTEK] {resource}: {e}")
            return None

    def get_or_create_feature(self, feature_name):
        if feature_name in self.feature_map: return self.feature_map[feature_name]
        schema = self._get_blank_schema('product_features')
        self._add_child(schema.find('product_feature'), 'name', feature_name)
        new_id = self.post_resource('product_features', schema)
        if new_id:
            self.feature_map[feature_name] = new_id
            return new_id
        return None

    def get_or_create_feature_value(self, feature_id, value_text):
        key = (feature_id, value_text)
        if key in self.feature_value_map: return self.feature_value_map[key]
        schema = self._get_blank_schema('product_feature_values')
        node = schema.find('product_feature_value')
        self._add_child(node, 'id_feature', feature_id)
        self._add_child(node, 'value', value_text)
        self._add_child(node, 'custom', '0')
        new_id = self.post_resource('product_feature_values', schema)
        if new_id:
            self.feature_value_map[key] = new_id
            return new_id
        return None

    def import_categories(self):
        print("\n--- IMPORT KATEGORII ---")
        if not os.path.exists(FILE_CATEGORIES):
            print(f"Brak pliku kategorii: {FILE_CATEGORIES}");
            return

        with open(FILE_CATEGORIES, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
            self.category_map["Strona główna"] = "2"
            for row in reader:
                if not row: continue
                name = row.get('Name')
                if not name or name in self.category_map: continue

                parent_name = row.get('Parent category')
                id_parent = self.category_map.get(parent_name, "2")
                schema = self._get_blank_schema('categories')
                node = schema.find('category')
                self._add_child(node, 'active', '1')
                self._add_child(node, 'id_parent', id_parent)
                self._add_child(node, 'name', name)
                self._add_child(node, 'link_rewrite', self._slugify(name))
                self._add_child(node, 'description', row.get('Description', ''))

                new_id = self.post_resource('categories', schema)
                if new_id:
                    self.category_map[name] = new_id
                    print(f"Kategoria '{name}' -> ID: {new_id}")

    def import_products(self):
        print("\n--- IMPORT PRODUKTÓW (BAZA) ---")
        if not os.path.exists(FILE_PRODUCTS):
            print(f"Brak pliku produktów: {FILE_PRODUCTS}");
            return

        with open(FILE_PRODUCTS, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
            for row in reader:
                if not row: continue
                name = row.get('Name')
                if not name or name == 'N/A': continue

                # 1. Parsowanie wszystkich kategorii z ciągu
                cat_string = row.get('Category', '')
                all_cats_raw = cat_string.split('|')

                # Zbieramy ID wszystkich pasujących kategorii do zbioru (set), żeby uniknąć duplikatów
                categories_to_assign = set()

                # Ustalanie głównej kategorii (ostatnia z listy)
                def_cat_name = all_cats_raw[-1].strip() if all_cats_raw else "Strona główna"
                id_cat_default = self.category_map.get(def_cat_name, "2")

                # Zawsze dodajemy kategorię domyślną do listy przypisań
                categories_to_assign.add(id_cat_default)

                # Iterujemy po wszystkich kategoriach w CSV i szukamy ich ID
                for c_raw in all_cats_raw:
                    c_clean = c_raw.strip()
                    if c_clean in self.category_map:
                        categories_to_assign.add(self.category_map[c_clean])

                # 2. Budowanie XML produktu
                schema = self._get_blank_schema('products')
                prod = schema.find('product')

                self._add_child(prod, 'name', name)
                self._add_child(prod, 'price', self._clean_price(row.get('Price')))
                self._add_child(prod, 'description', row.get('Description', ''))
                self._add_child(prod, 'id_category_default', id_cat_default)  # Kategoria główna
                self._add_child(prod, 'reference', row.get('Product ID', ''))
                self._add_child(prod, 'link_rewrite', self._slugify(name))

                self._add_child(prod, 'active', '1')
                self._add_child(prod, 'state', '1')
                self._add_child(prod, 'available_for_order', '1')
                self._add_child(prod, 'show_price', '1')

                self._add_child(prod, 'minimal_quantity', '1')
                self._add_child(prod, 'id_tax_rules_group', '1')
                self._add_child(prod, 'type', 'standard')
                self._add_child(prod, 'id_shop_default', '1')

                # 3. Przypisywanie WSZYSTKICH kategorii (Associations)
                associations = prod.find('associations')
                if associations is None: associations = ET.SubElement(prod, 'associations')

                # Usuń pusty tag <categories> jeśli istnieje
                for child in list(associations):
                    if child.tag == 'categories': associations.remove(child)

                cats_node = ET.SubElement(associations, 'categories')

                # Pętla po wszystkich znalezionych ID kategorii
                for cat_id in categories_to_assign:
                    c_item = ET.SubElement(cats_node, 'category')
                    ET.SubElement(c_item, 'id').text = str(cat_id)

                # 4. Cechy (Features)
                for child in list(associations):
                    if child.tag == 'product_features': associations.remove(child)
                feats_node = ET.SubElement(associations, 'product_features')
                for csv_col, ps_feat_name in FEATURE_MAPPING.items():
                    val = row.get(csv_col)
                    if val and val != 'N/A':
                        f_id = self.get_or_create_feature(ps_feat_name)
                        v_id = self.get_or_create_feature_value(f_id, val)
                        f_item = ET.SubElement(feats_node, 'product_feature')
                        ET.SubElement(f_item, 'id').text = str(f_id)
                        ET.SubElement(f_item, 'id_feature_value').text = str(v_id)

                # WYSYŁKA
                new_id = self.post_resource('products', schema)
                print(f"Utworzono produkt: {name[:40]}... (Kategorie: {len(categories_to_assign)})")


if __name__ == "__main__":
    importer = PrestaShopImporter(API_URL, API_KEY)
    importer.import_categories()
    importer.import_products()

    if PrestaUpdater:
        print("\n" + "=" * 50)
        print("IMPORT ZAKOŃCZONY. URUCHAMIAM AKTUALIZACJĘ (ZDJĘCIA/ILOŚCI)...")
        print("=" * 50 + "\n")
        updater = PrestaUpdater(API_URL, API_KEY)
        updater.CSV_FILE = FILE_PRODUCTS
        updater.run()
    else:
        print("\n[BŁĄD] Nie można uruchomić drugiego skryptu (brak pliku update_stock_and_images.py).")