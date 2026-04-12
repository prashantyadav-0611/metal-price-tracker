from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

import sqlite3

# Setup
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

URL = "https://www.metalscost.com/"
driver.get(URL)

wait = WebDriverWait(driver, 10)

target_ids = ["card-gold", "card-silver", "card-copper", "card-platinum"]

data = []

for metal_id in target_ids:
    try:
        card = wait.until(EC.presence_of_element_located((By.ID, metal_id)))

        name = card.find_element(By.CLASS_NAME, "metal-card-name").text
        price_text = card.find_element(By.CLASS_NAME, "metal-card-price").text

        price_text = price_text.replace("₹", "").replace(",", "").strip()

        if price_text:
            price = float(price_text)

            data.append({
                "metal": name,
                "price": price,
                "date": str(datetime.now().date())
            })

    except Exception as e:
        print(f"Error for {metal_id}: {e}")

driver.quit()

for d in data:
    print(d)
    

#database operations
conn = sqlite3.connect("metals.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS metals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metal TEXT,
    price REAL,
    date TEXT,
    UNIQUE(metal, date)
)
""")

for d in data:
    cursor.execute("""
        INSERT OR IGNORE INTO metals (metal, price, date)
        VALUES (?, ?, ?)
    """, (d["metal"], d["price"], d["date"]))

conn.commit()
conn.close()