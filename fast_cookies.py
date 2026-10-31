import json, glob, subprocess, re

files = sorted(glob.glob("Profil_*.json"))
print("=========================================================")
print("⚡ MISE À JOUR EXPRESS DES 21 PROFILS (SANS EXPORT JSON)")
print("Collez soit : c_user=1000...; xs=45%3A... (ou le JSON)")
print("Appuyez sur Entrée à vide pour garder le profil tel quel.")
print("Tapez 'q' + Entrée quand vous avez fini.")
print("=========================================================\n")

updated = 0
for f in files:
    raw = input(f"👉 {f} : ").strip()
    if raw.lower() == 'q':
        break
    if not raw:
        continue
    cookies = []
    if raw.startswith("[") or raw.startswith("{"):
        data = json.loads(raw)
        items = data if isinstance(data, list) else data.get("cookies", [])
        for c in items:
            if "name" in c and "value" in c:
                cookies.append({"name": c["name"], "value": c["value"], "domain": ".facebook.com", "path": "/", "secure": True})
    else:
        for pair in re.split(r'[;\n]+', raw):
            if '=' in pair:
                k, v = pair.strip().split('=', 1)
                cookies.append({"name": k.strip(), "value": v.strip(), "domain": ".facebook.com", "path": "/", "secure": True})
    if cookies:
        with open(f, "w", encoding="utf-8") as out:
            json.dump(cookies, out, indent=2)
        print(f"   ✅ {f} enregistré ({len(cookies)} cookies)")
        updated += 1

if updated > 0:
    print("\n🔐 Chiffrement dans accounts.enc et envoi sur GitHub...")
    subprocess.run('tar -czf accounts.tar.gz Profil_*.json && openssl enc -aes-256-cbc -pbkdf2 -in accounts.tar.gz -out accounts.enc -pass pass:"Fastlane2026" && rm -f accounts.tar.gz && echo "$(date)" > last_run.txt && git add accounts.enc Profil_*.json last_run.txt && git commit -m "Update cookies via script" && git push origin main', shell=True)
    print("🚀 TERMINÉ ! Vos profils sont à jour et l'opération est lancée sur GitHub Actions !")
