# Books Catalogue Scraper (books.toscrape.com)

A resilient, single-context Playwright scraping pipeline that extracts the entire 1000-book inventory from `books.toscrape.com`. It autonomously follows pagination to the catalogue's end and cleans the raw extraction into a strict schema using Pandas.

## Extracted Schema (`books.csv`)
1. **title** (string) — The full title of the book.
2. **price** (float) — The price in GBP (the `£` symbol is stripped during Pandas cleansing).
3. **rating** (integer) — Star rating from 1 to 5, mapped dynamically from CSS classes.
4. **availability** (string) — Stock status (e.g., "In stock").
5. **category** (string) — Extracted directly from the individual book's breadcrumb.
6. **product_url** (string) — Absolute URL uniquely identifying the product page.

## Pagination Strategy
The scraper does **not** rely on a hardcoded loop of 50 pages. Instead, it locates the `li.next > a` node at the bottom of the catalogue list. It evaluates the absolute URL of the next button and follows it sequentially until the element is no longer present on the page, ensuring it will naturally adapt if the inventory shrinks or expands.

To maintain the catalogue list state while acquiring the category for each book, the scraper utilizes two concurrent tabs within a single Playwright Browser Context — one holding the main list, and one querying the details page politely.

## Execution
```bash
# 1. Install dependencies
pip install playwright pandas pytest
playwright install chromium

# 2. Run the end-to-end scraper and verification test suite
bash run_demo.sh
```
