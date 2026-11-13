import re
import pandas as pd
from playwright.sync_api import sync_playwright

def scrape_hacker_news(output_csv: str = "hn_top30.csv"):
    with sync_playwright() as p:
        # CLANCY PATCH (VM egress): this VM's proxy 403s Chromium's direct
        # CONNECT, so route through the local relay_proxy.py (localhost:18082),
        # which forwards through the same egress proxy. See MASTER_CONTEXT.md.
        browser = p.chromium.launch(headless=True, args=["--ignore-certificate-errors"])
        ctx = browser.new_context(
            proxy={"server": "http://127.0.0.1:18082"}, ignore_https_errors=True
        )
        page = ctx.new_page()
        page.goto("https://news.ycombinator.com/")
        
        # HN uses a legacy table structure where title rows (.athing) and detail rows (.subtext) are siblings
        athings = page.locator(".athing").all()
        subtexts = page.locator("td.subtext").all()
        
        data = []
        
        # Zip them together to avoid fragile sibling XPath traversal, capping at top 30
        for item, subtext in zip(athings[:30], subtexts[:30]):
            # 1. Rank
            rank_str = item.locator(".rank").inner_text()
            rank = int(re.sub(r'\D', '', rank_str))
            
            # 2. Title
            title = item.locator(".titleline > a").first.inner_text().strip()
            
            # 3. Domain
            sitebit = item.locator(".sitebit")
            domain = sitebit.inner_text().strip(" ()") if sitebit.count() > 0 else ""
            
            # 4. Points
            score_el = subtext.locator(".score")
            points_str = score_el.inner_text() if score_el.count() > 0 else "0"
            points_match = re.search(r'\d+', points_str)
            points = int(points_match.group()) if points_match else 0
            
            # 5. Submitter
            # CLANCY FIX: HN's submitter link no longer carries the "hnuser"
            # class — it is a plain <a href="user?id=...">. Match by href.
            user_el = subtext.locator('a[href^="user?id="]')
            submitter = user_el.inner_text().strip() if user_el.count() > 0 else ""
            
            # 6. Comment Count
            links = subtext.locator("a").all()
            comments_str = links[-1].inner_text() if links else ""
            if "discuss" in comments_str or not comments_str:
                comment_count = 0
            else:
                comments_match = re.search(r'\d+', comments_str)
                comment_count = int(comments_match.group()) if comments_match else 0
                
            data.append({
                "rank": rank,
                "title": title,
                "domain": domain,
                "points": points,
                "submitter": submitter,
                "comment_count": comment_count
            })
            
        browser.close()
        
        # Enforce strict schema using Pandas
        df = pd.DataFrame(data)
        df['rank'] = df['rank'].astype(int)
        df['title'] = df['title'].astype(str)
        df['domain'] = df['domain'].astype(str)
        df['points'] = df['points'].astype(int)
        df['submitter'] = df['submitter'].astype(str)
        df['comment_count'] = df['comment_count'].astype(int)
        
        df.to_csv(output_csv, index=False)
        print(f"Successfully scraped and cleaned 30 records to {output_csv}")

if __name__ == "__main__":
    scrape_hacker_news()
