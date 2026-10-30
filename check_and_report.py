import os, json, glob
from playwright.sync_api import sync_playwright

proxy_str = os.environ.get("PROXY_TN", "").strip()
proxy_cfg = None
if proxy_str and "://" in proxy_str and "@" in proxy_str:
    proto, rest = proxy_str.split("://", 1)
    creds, hostport = rest.rsplit("@", 1)
    u, pw = creds.split(":", 1)
    import random, string, re
    sid = "".join(random.choices(string.ascii_letters + string.digits, k=8))
    pw = re.sub(r"_session-[^_]+", "", pw); pw = re.sub(r"_lifetime-[^_]+", "", pw)
    proxy_cfg = {"server": f"{proto}://{hostport}", "username": u, "password": pw}
    print(f"🌍 Proxy Tunisien activé : {proxy_cfg['server']}")

files = sorted(glob.glob("Profil_*.json"))
actifs, bloques = [], []

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled", "--no-sandbox"], proxy=proxy_cfg)
    for f in files:
        try:
            d = json.load(open(f))
            raw = d if isinstance(d, list) else d.get("cookies", [])
            c = [{"name": x["name"], "value": x["value"], "domain": ".facebook.com", "path": "/"} for x in raw if x.get("name") in ["c_user", "xs", "fr", "sb"]]
            ctx = b.new_context(locale="fr-FR")
            ctx.add_cookies(c)
            page = ctx.new_page()
            page.route("**/*", lambda r: r.abort() if r.request.resource_type in ["image", "media", "font"] or any(k in r.request.url.lower() for k in [".mp4", ".webm", ".avi", "video"]) else r.continue_()) if r.request.resource_type in ["image", "media", "font", "stylesheet", "other"] or any(k in r.request.url.lower() for k in [".mp4", ".jpg", ".png", ".webp", "video", "scontent", "fbcdn.net/v/"]) else r.continue_())
            page.goto("https://m.facebook.com/home.php", wait_until="domcontentloaded", timeout=25000)
            page.wait_for_timeout(2000)
            if "checkpoint" in page.url.lower() or "login" in page.url.lower():
                print(f"🔒 BLOQUÉ : {f}")
                bloques.append(f)
            else:
                print(f"✅ ACTIF  : {f}")
                actifs.append(f)
            ctx.close()
        except Exception as e:
            bloques.append(f)
    b.close()

print(f"\n📊 RÉSULTAT DES 21 PROFILS (IP TUNISIE) : {len(actifs)} ACTIFS / {len(bloques)} BLOQUÉS")
