from playwright.sync_api import sync_playwright
import json
import time
from pathlib import Path
from datetime import datetime
import logging
import os

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ------------------- Configs -------------------
URL = "https://www.seminovosmovida.com.br/busca"

# ✅ Path absoluto para Docker
OUTPUT_PATH = Path("/opt/airflow/data/bronze")
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

BATCH_SIZE = 100

# ------------------- Funções -------------------
def extract_car(car):
    if car.locator("a").count() == 0:
        return None
    link = car.locator("a").get_attribute("href")
    title = car.locator(".info__title").inner_text().strip()
    version = car.locator(".info__subtitle").inner_text().strip()
    details = car.locator(".add__info").inner_text().strip()
    parcela = car.locator(".fin").inner_text().strip()

    old_price = None
    new_price = None
    if car.locator(".price-24.tachado").count() > 0:
        old_price = car.locator(".price-24.tachado").inner_text().strip()
    if car.locator(".price-30").count() > 0:
        new_price = car.locator(".price-30").inner_text().strip()
    if new_price is None:
        new_price = car.locator(".price label").first.inner_text().strip()

    return {
        "link": "https://www.seminovosmovida.com.br" + link,
        "title": title, "version": version, "details": details,
        "old_price": old_price, "new_price": new_price, "parcela": parcela
    }


def save_batch(batch, idx):
    if not batch: return
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = OUTPUT_PATH / f"cars_batch_{idx}_{now}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(batch, f, ensure_ascii=False, indent=4)
    logging.info(f"Batch {idx} salvo: {len(batch)} carros → {file_path}")





def run_extraction():
    headless = os.environ.get("HEADLESS", "true").lower() == "true"

      # 🧹 LIMPAR ARQUIVOS ANTIGOS DA BRONZE
    if OUTPUT_PATH.exists():
        for old_file in OUTPUT_PATH.glob("*.json"):
            old_file.unlink()
            logging.info(f"Removido arquivo antigo: {old_file.name}")
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    logging.info("Pasta Bronze limpa e pronta para nova extração")

    with sync_playwright() as p:
        # ✅ Flags essenciais para Docker
        browser = p.chromium.launch(
            headless=headless,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",  # ← Previne crash de memória
                "--disable-gpu",
                "--disable-software-rasterizer"
            ]
        )
        page = browser.new_page()
        
        # ✅ User-Agent para evitar bloqueio
        page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        })
        
        # ✅ Timeout maior + wait_until mais rápido
        page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_selector("div.car", timeout=30000)

        batch, batch_idx, loaded = [], 1, 0

        while True:
            cars = page.locator("div.car")
            total = cars.count()

            for i in range(loaded, total):
                car_data = extract_car(cars.nth(i))
                if car_data: batch.append(car_data)
                if len(batch) >= BATCH_SIZE:
                    save_batch(batch, batch_idx)
                    batch_idx += 1
                    batch = []

            loaded = total
            old_height = page.evaluate("document.body.scrollHeight")
            page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            time.sleep(5)  # ← Reduzido de 10s para 5s
            new_height = page.evaluate("document.body.scrollHeight")
            if new_height == old_height: break

        if batch: save_batch(batch, batch_idx)
        browser.close()