with open("/workspaces/Fastlane/app.py", "r", encoding="utf-8") as f:
    code = f.read()

# Remplacement complet de la fonction de publication pour supporter Reels + Posts + Diagnostic précis
import re

new_worker = '''def run_bot(accounts, url, delay, comments):
    global logs
    url = url.strip().rstrip(",")
    clean_comments = [c.strip().lstrip("*").strip() for c in comments if c.strip().lstrip("*").strip()]
    if not clean_comments:
        logs.append("⚠️ Aucun commentaire valide trouvé.")
        return

    with sync_playwright() as p:
        for i, acc in enumerate(accounts):
            comment = clean_comments[i % len(clean_comments)]
            logs.append(f"☁️ Envoi avec {acc}...")
            try:
                browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled", "--no-sandbox"])
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                    viewport={"width": 1280, "height": 800},
                    locale="fr-FR"
                )
                
                acc_path = os.path.join(ACCOUNTS_DIR, acc if acc.endswith(".json") else acc + ".json")
                with open(acc_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                cookies = data.get("cookies", data) if isinstance(data, dict) else data
                
                valid_cookies = []
                for c in cookies:
                    if isinstance(c, dict) and "name" in c and "value" in c:
                        c_copy = {
                            "name": str(c["name"]),
                            "value": str(c["value"]),
                            "domain": c.get("domain", ".facebook.com"),
                            "path": c.get("path", "/"),
                            "secure": bool(c.get("secure", True)),
                            "httpOnly": bool(c.get("httpOnly", False))
                        }
                        valid_cookies.append(c_copy)
                context.add_cookies(valid_cookies)

                page = context.new_page()
                page.goto(url, wait_until="domcontentloaded", timeout=45000)
                page.wait_for_timeout(5000)

                # Accepter les cookies si popup
                for txt in ["Autoriser tous les cookies", "Allow all cookies", "Accepter", " Tout accepter"]:
                    try:
                        btn = page.locator(f'div[role="button"]:has-text("{txt}"), button:has-text("{txt}")').first
                        if btn.is_visible(timeout=1000):
                            btn.click()
                            page.wait_for_timeout(1500)
                    except:
                        pass

                # Vérifier si le compte est déconnecté
                if "login" in page.url.lower() or page.locator('input[name="email"], input[name="pass"]').count() > 0:
                    if page.locator('div[role="textbox"]').count() == 0:
                        logs.append(f"❌ {acc} : Compte déconnecté (session expirée)")
                        browser.close()
                        continue

                # Chercher la boîte commentaire directement
                box_selectors = [
                    'div[role="textbox"][contenteditable="true"]',
                    'div[aria-label*="comment" i][role="textbox"]',
                    'div[aria-label*="commentaire" i][role="textbox"]',
                    'div[aria-placeholder*="comment" i]',
                    'div[aria-placeholder*="commentaire" i]',
                    'div[role="textbox"]'
                ]

                box = None
                for sel in box_selectors:
                    loc = page.locator(sel).first
                    if loc.count() > 0 and loc.is_visible():
                        box = loc
                        break

                # Si non visible (ex: Reel ou Post fermé), cliquer sur l'icône Commenter
                if not box:
                    click_selectors = [
                        'div[aria-label*="Commenter" i][role="button"]',
                        'div[aria-label*="Comment" i][role="button"]',
                        'div[aria-label*="Leave a comment" i][role="button"]',
                        'span:has-text("Commenter")',
                        'span:has-text("Comment")',
                        'div[role="button"]:has-text("Commenter")',
                        'div[role="button"]:has-text("Comment")'
                    ]
                    for c_sel in click_selectors:
                        try:
                            btn = page.locator(c_sel).first
                            if btn.count() > 0 and btn.is_visible():
                                btn.click(force=True)
                                page.wait_for_timeout(3000)
                                break
                        except:
                            pass

                    # Re-chercher après clic
                    for sel in box_selectors:
                        loc = page.locator(sel).first
                        if loc.count() > 0 and loc.is_visible():
                            box = loc
                            break

                # Si toujours rien, raccourci clavier Facebook 'c' (ouvre/focus le commentaire sur Reels & Posts)
                if not box:
                    page.keyboard.press("c")
                    page.wait_for_timeout(2000)
                    for sel in box_selectors:
                        loc = page.locator(sel).first
                        if loc.count() > 0 and loc.is_visible():
                            box = loc
                            break

                if box:
                    box.click(force=True)
                    page.wait_for_timeout(800)
                    page.keyboard.insert_text(comment)
                    page.wait_for_timeout(1000)
                    page.keyboard.press("Enter")
                    page.wait_for_timeout(4000)
                    logs.append(f"✅ Publié sur {acc} !")
                else:
                    title = page.title()
                    logs.append(f"⚠️ {acc} : Boîte introuvable (Page: {title[:25]})")

                browser.close()
            except Exception as e:
                logs.append(f"❌ Erreur {acc} : {str(e)[:40]}")

            if i < len(accounts) - 1:
                time.sleep(int(delay))
    logs.append("🎉 Terminé ! Tous les comptes ont fini.")
'''

# Remplacer l'ancienne fonction run_bot dans app.py
pattern = r"def run_bot\(.*?(?=\n@app\.route|\nif __name__)"
if re.search(pattern, code, flags=re.DOTALL):
    code = re.sub(pattern, new_worker + "\n", code, flags=re.DOTALL)
    with open("/workspaces/Fastlane/app.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("✅ Nouveau moteur Reels & Posts installé avec succès !")
else:
    print("⚠️ Structure différente dans app.py, affichage du fichier :")
