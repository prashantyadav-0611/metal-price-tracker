from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import sqlite3

# ---------------- SETUP ----------------
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

URL = "https://www.metalscost.com/"
driver.get(URL)

wait = WebDriverWait(driver, 15)

target_ids = ["card-gold", "card-silver", "card-copper", "card-platinum"]

data = []

# ---------------- SCRAPING ----------------
for metal_id in target_ids:
    try:
        # Wait until price text is NOT empty (important for JS sites)
        wait.until(lambda d: d.find_element(By.ID, metal_id)
                   .find_element(By.CLASS_NAME, "metal-card-price").text.strip() != "")

        card = driver.find_element(By.ID, metal_id)

        name = card.find_element(By.CLASS_NAME, "metal-card-name").text
        price_text = card.find_element(By.CLASS_NAME, "metal-card-price").text

        price_text = price_text.replace("₹", "").replace(",", "").strip()

        price = float(price_text)

        data.append({
            "metal": name,
            "price": price,
            "date": str(datetime.now().date())
        })

    except Exception as e:
        print(f"Error for {metal_id}: {e}")

driver.quit()

# ---------------- DEBUG OUTPUT ----------------
print("Scraped Data:", data)

# ---------------- DATABASE ----------------
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

print("Database updated successfully")
