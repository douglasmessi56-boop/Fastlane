import json, glob
from playwright.sync_api import sync_playwright

files = sorted(glob.glob("Profil_*.json"))
actifs = []
bloques = []

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox"])
    for f in files:
        try:
            d = json.load(open(f))
            raw = d if isinstance(d, list) else d.get("cookies", [])
            c = []
            for x in raw:
                if x.get("name") in ["c_user", "xs", "fr", "sb"]:
                    c.append({"name": x["name"], "value": x["value"], "domain": ".facebook.com", "path": "/"})
            ctx = b.new_context()
            ctx.add_cookies(c)
            page = ctx.new_page()
            page.goto("https://m.facebook.com/home.php", wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(1500)
            u = page.url.lower()
            if "checkpoint" in u or "login" in u:
                print("BLOQUE :", f, "->", page.url[:50])
                bloques.append(f)
            else:
                print("ACTIF  :", f, "->", page.title()[:30])
                actifs.append(f)
            ctx.close()
        except Exception as e:
            print("ERREUR :", f)
            bloques.append(f)
    b.close()

print("==========================================")
print("BILAN :", len(actifs), "ACTIFS /", len(bloques), "BLOQUES")
print("LISTE ACTIFS :", actifs)
print("==========================================")
