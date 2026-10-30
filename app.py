import os, json, time, threading, re
from http.server import HTTPServer, BaseHTTPRequestHandler
from playwright.sync_api import sync_playwright

PORT = 8099
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ACCOUNTS_DIR = os.path.join(BASE_DIR, "Comptes_FB_Fastlane")
os.makedirs(ACCOUNTS_DIR, exist_ok=True)

logs = ["☁️ Serveur Cloud V3 (100% Reels + Watch Fallback) prêt !"]
is_running_job = False

HTML_PAGE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Fastlane">
<title>Fastlane Cloud V3</title>
<style>
  body { background:#0f172a; color:#f8fafc; font-family:-apple-system,sans-serif; margin:0; padding:15px; }
  .card { background:#1e293b; border:1px solid #334155; border-radius:14px; padding:16px; max-width:520px; margin:0 auto; box-shadow:0 10px 25px rgba(0,0,0,0.4); }
  h2 { margin-top:0; color:#38bdf8; text-align:center; font-size:20px; }
  label { display:block; margin:12px 0 6px; font-weight:600; font-size:14px; color:#cbd5e1; }
  input[type="text"], input[type="number"], textarea {
    width:100%; box-sizing:border-box; background:#0f172a; border:1px solid #475569;
    color:#fff; border-radius:8px; padding:10px; font-size:14px;
  }
  .acc-box { max-height:175px; overflow-y:auto; background:#0f172a; border:1px solid #334155; border-radius:8px; padding:8px; }
  .acc-item { display:flex; align-items:center; padding:8px 6px; border-bottom:1px solid #1e293b; font-size:14px; }
  .acc-item input { margin-right:10px; transform:scale(1.2); }
  .btn-row { display:flex; gap:8px; margin-bottom:8px; flex-wrap:wrap; }
  .btn-small { background:#334155; color:#fff; border:none; padding:6px 10px; border-radius:6px; font-size:12px; cursor:pointer; }
  .btn-main {
    width:100%; background:#0284c7; color:#fff; border:none; padding:14px;
    border-radius:10px; font-size:15px; font-weight:bold; margin-top:14px; cursor:pointer;
  }
  .console {
    background:#090d16; border:1px solid #334155; border-radius:8px; padding:12px;
    margin-top:14px; height:210px; overflow-y:auto; font-family:monospace; font-size:13px; line-height:1.5;
  }
</style>
</head>
<body>
<div class="card">
  <h2>⚡ Fastlane Cloud V3</h2>
  <label>👥 Comptes Facebook (<span id="count">0</span>) :</label>
  <div class="btn-row">
    <button class="btn-small" onclick="toggleAll(true)">Tout cocher</button>
    <button class="btn-small" onclick="toggleAll(false)">Tout décocher</button>
    <button class="btn-small" style="background:#dc2626;" onclick="decocherBloques()">Exclure Checkpoints connus</button>
  </div>
  <div class="acc-box" id="accList">Chargement...</div>

  <label>📌 Lien du Reel / Post Facebook :</label>
  <input type="text" id="url" placeholder="https://www.facebook.com/reel/..." oninput="saveForm()">

  <label>⏱️ Délai entre chaque compte (secondes) :</label>
  <input type="number" id="delay" value="45" oninput="saveForm()">

  <label>💬 Liste des commentaires (1 par ligne) :</label>
  <textarea id="comments" rows="5" oninput="saveForm()"></textarea>

  <button class="btn-main" onclick="lancer()">🚀 LANCER DEPUIS LE CLOUD (SANS PC)</button>
  <div class="console" id="logs"></div>
</div>

<script>
const BLOQUES = ["Profil_10_9.json", "Profil_12_11.json", "Profil_14_12.json", "Profil_16_15.json"];

function saveForm() {
  localStorage.setItem('fl_url', document.getElementById('url').value);
  localStorage.setItem('fl_delay', document.getElementById('delay').value);
  localStorage.setItem('fl_comments', document.getElementById('comments').value);
}

function restoreForm() {
  if(localStorage.getItem('fl_url')) document.getElementById('url').value = localStorage.getItem('fl_url');
  if(localStorage.getItem('fl_delay')) document.getElementById('delay').value = localStorage.getItem('fl_delay');
  if(localStorage.getItem('fl_comments')) document.getElementById('comments').value = localStorage.getItem('fl_comments');
}

async function chargerComptes() {
  const r = await fetch('/api/list');
  const d = await r.json();
  document.getElementById('count').innerText = d.accounts.length;
  const box = document.getElementById('accList');
  box.innerHTML = '';
  d.accounts.forEach(a => {
    const isOk = !BLOQUES.includes(a);
    box.innerHTML += `<label class="acc-item"><input type="checkbox" class="acc-chk" value="${a}" ${isOk ? 'checked' : ''}> 👤 ${a.replace('.json','')}</label>`;
  });
}
function toggleAll(state) {
  document.querySelectorAll('.acc-chk').forEach(c => c.checked = state);
}
function decocherBloques() {
  document.querySelectorAll('.acc-chk').forEach(c => {
    if(BLOQUES.includes(c.value)) c.checked = false;
  });
}
async function lancer() {
  saveForm();
  const accs = Array.from(document.querySelectorAll('.acc-chk:checked')).map(c => c.value);
  const url = document.getElementById('url').value;
  const delay = document.getElementById('delay').value;
  const comments = document.getElementById('comments').value;
  await fetch('/api/run', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({accounts:accs, url:url, delay:delay, comments:comments})
  });
}
async function majLogs() {
  try {
    const r = await fetch('/api/logs');
    const d = await r.json();
    const el = document.getElementById('logs');
    el.innerHTML = d.logs.join('<br>');
    el.scrollTop = el.scrollHeight;
  } catch(e) {}
}
setInterval(majLogs, 2000);
window.onload = () => { restoreForm(); chargerComptes(); majLogs(); };
</script>
</body>
</html>
"""

def load_cookies_into_context(context, acc):
    acc_path = os.path.join(ACCOUNTS_DIR, acc if acc.endswith(".json") else acc + ".json")
    with open(acc_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    cookies = data.get("cookies", data) if isinstance(data, dict) else data
    valid_cookies = []
    for c in cookies:
        if isinstance(c, dict) and "name" in c and "value" in c:
            valid_cookies.append({
                "name": str(c["name"]),
                "value": str(c["value"]),
                "domain": ".facebook.com",
                "path": "/",
                "secure": True
            })
    context.add_cookies(valid_cookies)

def try_post_comment(page, comment):
    for txt in ["Autoriser tous les cookies", "Allow all cookies", "Accepter", "Tout accepter", "Continuer", "Continue"]:
        try:
            b = page.locator(f'div[role="button"]:has-text("{txt}"), button:has-text("{txt}")').first
            if b.count() > 0 and b.is_visible():
                b.click(force=True)
                page.wait_for_timeout(1200)
        except:
            pass

    page.mouse.wheel(0, 400)
    page.wait_for_timeout(1500)

    box_sels = [
        'div[role="textbox"][contenteditable="true"]',
        'div[aria-label*="comment" i][role="textbox"]',
        'div[aria-label*="commentaire" i][role="textbox"]',
        'div[aria-label*="Écrivez" i][role="textbox"]',
        'div[aria-label*="Write" i][role="textbox"]',
        'textarea[name="comment_text"]',
        'textarea',
        'div[role="textbox"]'
    ]

    for attempt in range(3):
        for s in box_sels:
            try:
                loc = page.locator(s).first
                if loc.count() > 0 and loc.is_visible():
                    loc.scroll_into_view_if_needed()
                    loc.click(force=True)
                    page.wait_for_timeout(800)
                    page.keyboard.insert_text(comment)
                    page.wait_for_timeout(1000)
                    page.keyboard.press("Enter")
                    page.wait_for_timeout(4000)
                    return True
            except:
                pass

        btn_sels = [
            'div[aria-label*="Commenter" i][role="button"]',
            'div[aria-label*="Comment" i][role="button"]',
            'div[aria-label*="commentaires" i][role="button"]',
            'div[aria-label*="comments" i][role="button"]',
            'div[aria-label*="Leave a comment" i][role="button"]',
            'span:has-text("Commenter")',
            'span:has-text("Comment")'
        ]
        for bs in btn_sels:
            try:
                btn = page.locator(bs).first
                if btn.count() > 0 and btn.is_visible():
                    btn.click(force=True)
                    page.wait_for_timeout(2500)
                    break
            except:
                pass
        page.keyboard.press("c")
        page.wait_for_timeout(2000)

    return False

def run_bot(accounts, url, delay, raw_comments):
    global logs, is_running_job
    if is_running_job:
        logs.append("⚠️ Un envoi est déjà en cours...")
        return
    is_running_job = True
    try:
        url = url.strip().rstrip(",").strip()
        comments = [re.sub(r'^[\*\-\•\s]+|[\*\s]+$', '', c).strip() for c in raw_comments.split("\n")]
        comments = [c for c in comments if c]
        if not url or not comments:
            logs.append("⚠️ Vérifie le lien et les commentaires.")
            is_running_job = False
            return

        with sync_playwright() as p:
            for i, acc in enumerate(accounts):
                comment = comments[i % len(comments)]
                name_clean = acc.replace(".json", "")
                logs.append(f"☁️ Envoi avec {name_clean}...")
                published_ok = False
                try:
                    browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled", "--no-sandbox"])
                    context = browser.new_context(
                        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                        viewport={"width": 1280, "height": 800},
                        locale="fr-FR"
                    )
                    load_cookies_into_context(context, acc)
                    page = context.new_page()
                    page.goto(url, wait_until="domcontentloaded", timeout=45000)
                    page.wait_for_timeout(5000)

                    u = page.url.lower()
                    if "checkpoint" in u:
                        logs.append(f"🔴 {name_clean} : Checkpoint (sauté sans attendre)")
                        browser.close()
                        continue
                    if "login" in u:
                        logs.append(f"⚪ {name_clean} : Session expirée (sauté)")
                        browser.close()
                        continue

                    # 1er essai sur l'URL directe (Reel ou Post)
                    ok = try_post_comment(page, comment)

                    # 2e essai automatique : si c'est un Reel dont le volet est fermé, basculer en mode Watch/Post
                    if not ok:
                        m = re.search(r'/reel/(\d+)', page.url)
                        if m:
                            reel_id = m.group(1)
                            watch_url = f"https://www.facebook.com/watch/?v={reel_id}"
                            page.goto(watch_url, wait_until="domcontentloaded", timeout=35000)
                            page.wait_for_timeout(4500)
                            ok = try_post_comment(page, comment)

                    # 3e essai universel (Posts & Reels) via mbasic.facebook.com (formulaire HTML direct)
                    if not ok:
                        mbasic_url = re.sub(r'^https?://(www\.|m\.)?facebook\.com', 'https://mbasic.facebook.com', url)
                        page.goto(mbasic_url, wait_until="domcontentloaded", timeout=35000)
                        page.wait_for_timeout(3500)
                        try:
                            ta = page.locator('textarea[name="comment_text"], textarea').first
                            if ta.count() > 0:
                                ta.fill(comment)
                                page.wait_for_timeout(800)
                                sub = page.locator('input[type="submit"], button[type="submit"]').first
                                if sub.count() > 0:
                                    sub.click(force=True)
                                    page.wait_for_timeout(3500)
                                    ok = True
                        except:
                            pass
                        if not ok:
                            ok = try_post_comment(page, comment)

                    if ok:
                        logs.append(f"✅ Publié avec {name_clean} !")
                        published_ok = True
                    else:
                        cur = page.url.replace("https://www.facebook.com", "")[:32]
                        logs.append(f"⚠️ {name_clean} : Non trouvé sur {cur}")

                    browser.close()
                except Exception as e:
                    logs.append(f"❌ {name_clean} : {str(e)[:35]}")

                if published_ok and i < len(accounts) - 1:
                    time.sleep(int(delay))
        logs.append("🎉 Terminé ! Tous les comptes ont fini.")
    finally:
        is_running_job = False

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return
    def do_GET(self):
        if self.path.startswith("/api/list"):
            files = sorted([f for f in os.listdir(ACCOUNTS_DIR) if f.endswith(".json")])
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"accounts": files}).encode())
        elif self.path.startswith("/api/logs"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"logs": logs[-50:]}).encode())
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(length).decode("utf-8")) if length > 0 else {}
        if self.path.startswith("/api/run"):
            threading.Thread(target=run_bot, args=(
                data.get("accounts", []),
                data.get("url", ""),
                data.get("delay", 45),
                data.get("comments", "")
            ), daemon=True).start()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "started"}).encode())

if __name__ == "__main__":
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
