import re
import time
import pandas as pd
from playwright.sync_api import sync_playwright

def scrape_books_catalogue(output_csv: str = "books.csv"):
    books_data = []
    
    with sync_playwright() as p:
        # CLANCY PATCH (VM egress): this VM's proxy 403s Chromium's direct
        # CONNECT, so route through the local relay_proxy.py (localhost:18082),
        # which forwards through the same egress proxy.
        browser = p.chromium.launch(headless=True, args=["--ignore-certificate-errors"])
        ctx = browser.new_context(
            proxy={"server": "http://127.0.0.1:18082"},
            ignore_https_errors=True
        )
        
        # We use one page for the main catalogue loop, and a second for detail pages 
        # to preserve our list state without navigating back and forth.
        list_page = ctx.new_page()
        detail_page = ctx.new_page()
        
        current_url = "https://books.toscrape.com/"
        list_page.goto(current_url)
        
        rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        
        while True:
            list_page.wait_for_selector('article.product_pod')
            pods = list_page.locator('article.product_pod').all()
            
            for pod in pods:
                # 1. Title
                title_el = pod.locator('h3 > a')
                title = title_el.get_attribute('title')
                if not title:
                    title = title_el.inner_text().strip()
                
                # 2. Price
                price_str = pod.locator('.price_color').inner_text()
                
                # 3. Rating
                rating_class = pod.locator('.star-rating').get_attribute('class') or ""
                rating = 0
                for key, val in rating_map.items():
                    if key in rating_class:
                        rating = val
                        break
                        
                # 4. Availability
                availability = pod.locator('.instock.availability').inner_text().strip()
                
                # 5. Product URL (absolute resolution)
                product_url = title_el.evaluate("el => el.href")
                
                # 6. Category (from detail page)
                detail_page.goto(product_url)
                detail_page.wait_for_selector('ul.breadcrumb')
                category = detail_page.locator('ul.breadcrumb li:nth-child(3) a').inner_text().strip()
                
                books_data.append({
                    "title": title,
                    "price": price_str,
                    "rating": rating,
                    "availability": availability,
                    "category": category,
                    "product_url": product_url
                })
                
                time.sleep(0.1)  # polite delay between detail requests
                
            # Pagination logic: discover end by presence of "next" button
            next_btn = list_page.locator('li.next > a')
            if next_btn.count() > 0:
                next_url = next_btn.first.evaluate("el => el.href")
                list_page.goto(next_url)
                time.sleep(0.5)  # polite delay between page turns
            else:
                break
                
        browser.close()
        
    # Enforce strict schema using Pandas
    df = pd.DataFrame(books_data)
    
    df['title'] = df['title'].astype(str)
    # Strip the £ sign and convert to float
    df['price'] = df['price'].astype(str).str.replace(r'[^\d.]', '', regex=True).astype(float)
    df['rating'] = df['rating'].astype(int)
    df['availability'] = df['availability'].astype(str)
    df['category'] = df['category'].astype(str)
    df['product_url'] = df['product_url'].astype(str)
    
    # Drop completely null critical rows if any exist
    df.dropna(subset=['title', 'price', 'rating', 'category'], inplace=True)
    
    df.to_csv(output_csv, index=False)
    print(f"Successfully scraped and cleaned {len(df)} records to {output_csv}")

if __name__ == "__main__":
    scrape_books_catalogue()
