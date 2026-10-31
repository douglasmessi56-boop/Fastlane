import urllib.request, json, time, subprocess, glob
from playwright.sync_api import sync_playwright

API = "http://local.adspower.net:50325"
req = urllib.request.urlopen(f"{API}/api/v1/user/list?page_size=50")
users = json.loads(req.read().decode())["data"]["list"]

print(f"🔍 {len(users)} profils trouvés dans AdsPower.")
idx = 1

with sync_playwright() as p:
    for u in users:
        if idx > 21:
            break
        uid = u["user_id"]
        r = json.loads(urllib.request.urlopen(f"{API}/api/v1/browser/start?user_id={uid}&open_tabs=1&headless=1").read().decode())
        if r.get("code") == 0:
            ws = r["data"]["ws"]["puppeteer"]
            browser = p.chromium.connect_over_cdp(ws)
            cookies = [c for c in browser.contexts[0].cookies() if "facebook.com" in c.get("domain", "")]
            c_user = [c["value"] for c in cookies if c["name"] == "c_user"]
            if c_user:
                fname = f"Profil_{idx}_{uid}.json"
                with open(fname, "w") as f:
                    json.dump(cookies, f, indent=2)
                print(f"✅ [{idx}/21] {fname} extrait (c_user: {c_user[0]})")
                idx += 1
            else:
                print(f"⚠️ Profil {uid} non connecté à Facebook, ignoré.")
            browser.close()
            urllib.request.urlopen(f"{API}/api/v1/browser/stop?user_id={uid}")
            time.sleep(1.5)

subprocess.run('tar -czf accounts.tar.gz Profil_*.json && openssl enc -aes-256-cbc -pbkdf2 -in accounts.tar.gz -out accounts.enc -pass pass:"Fastlane2026"', shell=True)
print("\n🎉 Fichier accounts.enc généré sur votre Mac avec tous vos profils AdsPower !")
