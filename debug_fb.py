import json
from playwright.sync_api import sync_playwright

with open("Profil_1_DefaultProfile.json", "r") as f:
    data = json.load(f)
cookies = data if isinstance(data, list) else data.get("cookies", [])

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    ctx.add_cookies(cookies)
    page = ctx.new_page()
    page.goto("https://www.facebook.com/100067225894838/posts/1424477049689595", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(4000)
    print("1. URL FINALE :", page.url)
    print("2. TITRE :", page.title())
    body = page.locator("body").inner_text()
    print("3. TEXTE VISIBLE :", " | ".join([l.strip() for l in body.splitlines() if l.strip()][:12]))
    print("4. NB TEXTBOX :", page.locator('[role="textbox"], [contenteditable="true"], textarea').count())
    b.close()
