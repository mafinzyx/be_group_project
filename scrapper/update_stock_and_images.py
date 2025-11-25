import csv
import requests
import xml.etree.ElementTree as ET
import random
import time
from io import BytesIO

# --- KONFIGURACJA ---
API_URL = "http://127.0.0.1/api"
API_KEY = "R7FM7TCGA6NJRJU49MFTSJDP2JQ481U1" 
CSV_FILE = "./data/products.csv"

class PrestaUpdater:
    def __init__(self, api_url, api_key):
        self.api_url = api_url.rstrip('/')
        self.session = requests.Session()
        self.session.auth = (api_key, '')
        self.session.verify = False

    def find_product_id_by_name(self, name):
        """Szuka ID produktu po nazwie."""
        try:
            url = f"{self.api_url}/products?display=[id,name]&filter[name]={name}"
            r = self.session.get(url)
            if r.status_code == 200:
                tree = ET.fromstring(r.content)
                products = tree.find('products')
                if products is not None and len(products) > 0:
                    return products[0].find('id').text
        except Exception as e:
            print(f"Błąd szukania produktu: {e}")
        return None

    def update_stock(self, product_id, quantity):
        """Aktualizuje stan magazynowy."""
        print(f"   [Stock] Aktualizacja dla ID {product_id} na {quantity} szt...")
        
        self._ensure_product_is_standard(product_id)

        try:
            url = f"{self.api_url}/stock_availables?display=full&filter[id_product]={product_id}"
            r = self.session.get(url)
            tree = ET.fromstring(r.content)
            
            stock_node = tree.find('stock_availables').find('stock_available')
            if stock_node is None:
                print("   [Stock] Błąd: Nie znaleziono rekordu magazynowego.")
                return

            stock_id = stock_node.find('id').text
            
            stock_node.find('quantity').text = str(quantity)
            
            if stock_node.find('id_shop') is None:
                ET.SubElement(stock_node, 'id_shop').text = '1'
            else:
                stock_node.find('id_shop').text = '1'

            payload = ET.Element('prestashop')
            payload.append(stock_node)
            
            put_url = f"{self.api_url}/stock_availables/{stock_id}"
            put_r = self.session.put(put_url, data=ET.tostring(payload, encoding='utf-8'))
            
            if put_r.status_code == 200:
                print("   [Stock] Sukces.")
            else:
                print(f"   [Stock] Błąd API: {put_r.status_code}")

        except Exception as e:
            print(f"   [Stock] Wyjątek: {e}")

    def _ensure_product_is_standard(self, product_id):
        """Upewnia się, że produkt ma typ 'standard'."""
        try:
            url = f"{self.api_url}/products/{product_id}"
            r = self.session.get(url)
            tree = ET.fromstring(r.content)
            product = tree.find('product')
            
            current_type = product.find('type').text
            if current_type != 'standard': 
                product.find('type').text = 'standard' 
                payload = ET.Element('prestashop')
                payload.append(product)
                self.session.put(url, data=ET.tostring(payload, encoding='utf-8'))
        except:
            pass

    def upload_image(self, product_id, img_url):
        """Wgrywa zdjęcie."""
        if not img_url or 'http' not in img_url:
            return

        print(f"   [Foto] Pobieranie: {img_url}...")
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            img_r = requests.get(img_url, headers=headers, timeout=10)
            
            if img_r.status_code == 200:
                
                files = {
                    'image': ('image.jpg', BytesIO(img_r.content), 'image/jpeg')
                }
                post_url = f"{self.api_url}/images/products/{product_id}"
                
                r = self.session.post(post_url, files=files)
                
                if r.status_code == 200:
                    print("   [Foto] Wgrano pomyślnie.")
                else:
                    print(f"   [Foto] Błąd PrestaShop: {r.status_code}")
            else:
                print(f"   [Foto] Błąd pobierania z URL: {img_r.status_code}")
        except Exception as e:
            print(f"   [Foto] Wyjątek: {e}")

    def run(self):
        print("--- ROZPOCZYNAM AKTUALIZACJĘ ---")
        with open(CSV_FILE, newline='', encoding='utf-8') as csvfile: 
            reader = csv.DictReader(csvfile, delimiter=';') 

            for row in reader:
                name = row.get('Name')
                if not name: continue
                
                print(f"Przetwarzanie: {name[:40]}...")
                
                p_id = self.find_product_id_by_name(name)
                
                if p_id:
                    qty = random.randint(0, 10)
                    self.update_stock(p_id, qty)
                    
                    
                    self.upload_image(p_id, row.get('Image 1 URL (Hi-Res)'))
                    
                else:
                    print("   -> Nie znaleziono produktu w sklepie (może inna nazwa?)")

if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings()
    updater = PrestaUpdater(API_URL, API_KEY)
    updater.run()