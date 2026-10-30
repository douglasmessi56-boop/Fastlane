with open("/workspaces/Fastlane/app.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Nettoyer les puces "* " au début des commentaires
code = code.replace(
    "[c.strip() for c in data.get('comments', '').split('\\n') if c.strip()]",
    "[c.strip().lstrip('*').strip() for c in data.get('comments', '').split('\\n') if c.strip().lstrip('*').strip()]"
)

# 2. Améliorer la détection de la boîte commentaire sur les Reels Facebook
old_box_logic = "box = page.locator('div[role=\"textbox\"]').first"
new_box_logic = """
                # Fermer d'éventuels popups cookies
                for txt in ["Autoriser tous les cookies", "Allow all cookies", "Accepter"]:
                    try:
                        btn = page.locator(f'div[role="button"]:has-text("{txt}"), button:has-text("{txt}")').first
                        if btn.is_visible(timeout=1500):
                            btn.click()
                            page.wait_for_timeout(1000)
                    except:
                        pass

                # Ouvrir le panneau de commentaires si c'est un Reel
                box = page.locator('div[role="textbox"][contenteditable="true"], div[aria-label*="comment" i][role="textbox"], div[aria-label*="commentaire" i][role="textbox"], div[role="textbox"]').first
                if not box.is_visible(timeout=3000):
                    for sel in [
                        'div[aria-label*="Commenter" i][role="button"]',
                        'div[aria-label*="Comment" i][role="button"]',
                        'div[aria-label*="commentaire" i][role="button"]',
                        'span:has-text("Commenter")',
                        'span:has-text("Comment")'
                    ]:
                        try:
                            c_btn = page.locator(sel).first
                            if c_btn.is_visible(timeout=1500):
                                c_btn.click()
                                page.wait_for_timeout(2500)
                                break
                        except:
                            pass
                    box = page.locator('div[role="textbox"][contenteditable="true"], div[role="textbox"]').first
"""

if "Ouvrir le panneau de commentaires" not in code and old_box_logic in code:
    code = code.replace(old_box_logic, new_box_logic)

with open("/workspaces/Fastlane/app.py", "w", encoding="utf-8") as f:
    f.write(code)

print("✅ Mise à jour Spéciale Reels appliquée avec succès !")
