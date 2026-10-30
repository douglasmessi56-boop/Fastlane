import json
from playwright.sync_api import sync_playwright

with open("Profil_10_9.json", "r") as f:
    data = json.load(f)
raw_cookies = data if isinstance(data, list) else data.get("cookies", [])

# Ne garder que les cookies d'authentification propres pour éviter le crash "Something went wrong"
clean_cookies = []
for c in raw_cookies:
    if c.get("name") in ["c_user", "xs", "fr", "sb"]:
        clean_cookies.append({
            "name": c["name"],
            "value": c["value"],
            "domain": ".facebook.com",
            "path": "/"
        })

print("Cookies injectés :", [c["name"] for c in clean_cookies])

with sync_playwright() as p:
    b = p.chromium.launch(
        headless=True,
        args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
    )
    # Test 1 : Interface Desktop propre sans faux User-Agent contradictoire
    ctx = b.new_context(viewport={"width": 1280, "height": 800}, locale="fr-FR")
    ctx.add_cookies(clean_cookies)
    page = ctx.new_page()
    
    for domain in ["https://www.facebook.com", "https://m.facebook.com", "https://mbasic.facebook.com"]:
        url = f"{domain}/100067225894838/posts/1424477049689595"
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3500)
        nb = page.locator('[role="textbox"], [contenteditable="true"], textarea, input[name="comment_text"]').count()
        body_sample = " | ".join([l.strip() for l in page.locator("body").inner_text().splitlines() if l.strip()][:6])
        print(f"\n--- TEST {domain} ---")
        print("URL:", page.url[:70])
        print("TITRE:", page.title())
        print("CHAMPS TROUVÉS:", nb)
        print("APERÇU:", body_sample[:140])
    b.close()
