import os, re, json, random, time, subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
import auto_daily_bot as bot

POSTS_MAP = {}
COMMS_MAP = {}

for name, val in vars(bot).items():
    if name.startswith("__") or not isinstance(val, dict):
        continue
    sample_val = next(iter(val.values()), None)
    if isinstance(sample_val, list) and sample_val and isinstance(sample_val[0], str):
        if "http" in sample_val[0]:
            POSTS_MAP = val
        else:
            COMMS_MAP = val
    elif isinstance(sample_val, dict):
        for k, v in val.items():
            if isinstance(v, dict):
                if "posts" in v or "urls" in v or "links" in v:
                    POSTS_MAP[k] = v.get("posts") or v.get("urls") or v.get("links") or []
                if "comments" in v or "messages" in v:
                    COMMS_MAP[k] = v.get("comments") or v.get("messages") or []

PREF = ["", "Slm, ", "Brabi ", "Wallahi ", "Machallah ", "Ya3tikom essaha, ", "Bonsoir, ", "Bellehi ", "Franchement ", "A3az produit, "]
SUFF = [" 🙏", " ❤️", " 👍", " ✨", " svp ?", " merci !", " bravo 👏", " 🔥", ""]

def gen_20_unique_comments(base_list):
    results = []
    used = set()
    pool = list(base_list) if base_list else ["Barcha 3bed chakkrouh, chnowa soumou svp ?"]
    for _ in range(20):
        for _attempt in range(30):
            b = random.choice(pool)
            p = random.choice(PREF)
            s = random.choice(SUFF)
            if p and not b.lower().startswith(p.strip().lower()):
                txt = f"{p}{b[0].lower() + b[1:] if len(b) > 1 else b}{s}".strip()
            else:
                txt = f"{b}{s}".strip()
            if txt not in used:
                used.add(txt)
                break
        results.append(txt)
    return results

def get_data():
    out = {}
    for k, posts in POSTS_MAP.items():
        comms = COMMS_MAP.get(k, [])
        if not comms and COMMS_MAP:
            comms = next(iter(COMMS_MAP.values()))
        out[k] = {
            "posts": posts,
            "generated_per_post": [gen_20_unique_comments(comms) for _ in range(len(posts))]
        }
    return out

HTML = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Fastlane Générateur - 63 Posts x 20 Commentaires</title>
<style>
  body { font-family: system-ui, sans-serif; background: #0f172a; color: #fff; margin: 0; padding: 20px; }
  .top { background: #1e293b; padding: 20px; border-radius: 12px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; border: 1px solid #334155; position: sticky; top: 10px; z-index: 10; box-shadow: 0 8px 20px rgba(0,0,0,0.5); }
  button { cursor: pointer; border: none; padding: 12px 20px; border-radius: 8px; font-weight: bold; font-size: 14px; }
  .btn-gen { background: #3b82f6; color: #fff; }
  .btn-go { background: #10b981; color: #052e16; font-size: 16px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); gap: 16px; margin-top: 20px; }
  .card { background: #1e293b; padding: 15px; border-radius: 10px; border: 1px solid #334155; }
  .card h3 { margin: 0 0 12px 0; color: #fbbf24; display: flex; justify-content: space-between; border-bottom: 1px solid #334155; padding-bottom: 8px; }
  .post-block { background: #0f172a; padding: 10px; border-radius: 8px; margin-bottom: 12px; border-left: 3px solid #38bdf8; }
  .url { color: #60a5fa; font-size: 12px; font-weight: bold; word-break: break-all; margin-bottom: 6px; display: block; }
  details { font-size: 12px; color: #cbd5e1; }
  summary { cursor: pointer; color: #34d399; font-weight: bold; margin-bottom: 6px; }
  .comm-item { padding: 4px 8px; background: #1e293b; border-radius: 4px; margin-bottom: 4px; font-size: 12px; }
  #status { margin-top: 15px; padding: 14px; background: #064e3b; color: #a7f3d0; border-radius: 8px; display: none; font-weight: bold; }
</style>
</head>
<body>
  <div class="top">
    <div>
      <h2 style="margin:0;color:#38bdf8;">🚀 Application Fastlane — 63 Publications × 20 Commentaires (1 260 total)</h2>
      <div style="color:#94a3b8;font-size:13px;margin-top:4px;">⏱ 40 secondes d'écart entre chaque commentaire • 🇹🇳 Proxy Tunisien • 💻 Continue même Mac fermé</div>
    </div>
    <div style="display:flex;gap:10px;">
            <button class="btn-gen" style="background:#f59e0b;color:#000;" onclick="document.getElementById('cookieModal').style.display='block'">🍪 Mettre à jour les Profils (Cookies)</button>
      <button class="btn-gen" onclick="loadApp()">🔄 Régénérer les 1 260 Commentaires</button>
      <button class="btn-go" onclick="startCloud()">▶️ LANCER L'OPÉRATION SUR LES 63 PUBLICATIONS</button>
    </div>
  </div>
    <div id="cookieModal" style="display:none;background:#1e293b;padding:20px;border-radius:12px;margin-top:15px;border:2px solid #f59e0b;">
    <h3 style="margin-top:0;color:#fbbf24;">🍪 Remplacer les Cookies d'un Profil (Export Cookie-Editor / AdsPower)</h3>
    <select id="profName" style="padding:10px;border-radius:6px;width:260px;margin-bottom:10px;font-weight:bold;">
      <option value="Profil_1_DefaultProfile.json">Profil 1</option>
      <option value="Profil_2_kliesocq.json">Profil 2</option>
      <option value="Profil_3_2.json">Profil 3</option>
      <option value="Profil_4_3.json">Profil 4</option>
      <option value="Profil_5_4.json">Profil 5</option>
      <option value="Profil_6_5.json">Profil 6</option>
      <option value="Profil_7_6.json">Profil 7</option>
      <option value="Profil_8_7.json">Profil 8</option>
      <option value="Profil_9_8.json">Profil 9</option>
      <option value="Profil_10_9.json">Profil 10</option>
      <option value="Profil_11_10.json">Profil 11</option>
      <option value="Profil_12_11.json">Profil 12</option>
      <option value="Profil_13_13.json">Profil 13</option>
      <option value="Profil_14_12.json">Profil 14</option>
      <option value="Profil_15_14.json">Profil 15</option>
      <option value="Profil_16_15.json">Profil 16</option>
      <option value="Profil_17_16.json">Profil 17</option>
      <option value="Profil_18_17.json">Profil 18</option>
      <option value="Profil_19_18.json">Profil 19</option>
      <option value="Profil_20_19.json">Profil 20</option>
      <option value="Profil_21_20.json">Profil 21</option>
    </select>
    <textarea id="cookieJson" rows="6" style="width:100%;border-radius:8px;padding:10px;background:#0f172a;color:#38bdf8;border:1px solid #334155;" placeholder='Collez ici le JSON exporté de Cookie-Editor (ex: [{"name":"c_user", ...}])'></textarea>
    <div style="margin-top:10px;display:flex;gap:10px;">
      <button class="btn-go" onclick="saveCookie()">💾 Enregistrer & Chiffrer dans accounts.enc</button>
      <button class="btn-gen" style="background:#475569;" onclick="document.getElementById('cookieModal').style.display='none'">Fermer</button>
    </div>
  </div>
  <div id="status"></div>
  <div id="grid" class="grid"></div>
<script>
async function loadApp() {
  const r = await fetch('/api/gen?t=' + Date.now());
  const d = await r.json();
  const g = document.getElementById('grid');
  g.innerHTML = '';
  for (const [cat, info] of Object.entries(d)) {
    let postsHtml = '';
    info.posts.forEach((u, i) => {
      const cList = (info.generated_per_post[i] || []).map((c, idx) => `<div class="comm-item"><b>#${idx+1}</b> (⏱ +${idx*40}s) : ${c}</div>`).join('');
      postsHtml += `
        <div class="post-block">
          <a class="url" href="${u}" target="_blank">🔗 Publication #${i+1} : ${u.slice(0, 55)}...</a>
          <details>
            <summary>👁 Voir les 20 nouveaux commentaires générés (écart 40s)</summary>
            ${cList}
          </details>
        </div>`;
    });
    g.innerHTML += `<div class="card"><h3><span>📦 ${cat}</span><span>${info.posts.length} posts × 20 comm.</span></h3>${postsHtml}</div>`;
  }
}
async function saveCookie() {
  const p = document.getElementById('profName').value;
  const c = document.getElementById('cookieJson').value;
  const st = document.getElementById('status');
  st.style.display = 'block';
  st.innerText = '⏳ Enregistrement et chiffrement de ' + p + '...';
  const r = await fetch('/api/cookie', {method:'POST', body: JSON.stringify({profile: p, cookies: c})});
  st.innerText = await r.text();
}
async function startCloud() {
  const st = document.getElementById('status');
  st.style.display = 'block';
  st.innerText = '⏳ Démarrage des 63 publications × 20 commentaires (40s écart, Proxy Tunisien) en cours...';
  const r = await fetch('/api/start', {method:'POST'});
  st.innerText = await r.text();
}
loadApp();
</script>
</body>
</html>"""

class AppHandler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        if self.path.startswith("/api/gen"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(get_data(), ensure_ascii=False).encode("utf-8"))
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML.encode("utf-8"))
    def do_POST(self):
        if self.path.startswith("/api/upload_enc"):
            length = int(self.headers.get('Content-Length', 0))
            data = self.rfile.read(length)
            with open("accounts.enc", "wb") as f:
                f.write(data)
            subprocess.run('tar -xzf accounts.tar.gz 2>/dev/null || true', shell=True)
            subprocess.run('echo "$(date)" > last_run.txt && git add accounts.enc last_run.txt && git commit -m "Auto-sync AdsPower cookies" && git push origin main', shell=True)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
            return
        if self.path.startswith("/api/cookie"):
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length).decode('utf-8'))
            p_name = body["profile"]
            raw_c = json.loads(body["cookies"])
            cookies = raw_c if isinstance(raw_c, list) else raw_c.get("cookies", [])
            clean = []
            for ck in cookies:
                if "name" in ck and "value" in ck:
                    clean.append({
                        "name": ck["name"],
                        "value": ck["value"],
                        "domain": ck.get("domain", ".facebook.com"),
                        "path": ck.get("path", "/"),
                        "secure": True,
                        "httpOnly": ck.get("httpOnly", False),
                        "sameSite": "None"
                    })
            with open(p_name, "w", encoding="utf-8") as f:
                json.dump(clean, f, indent=2)
            subprocess.run('tar -czf accounts.tar.gz Profil_*.json && openssl enc -aes-256-cbc -pbkdf2 -in accounts.tar.gz -out accounts.enc -pass pass:"Fastlane2026" && rm -f accounts.tar.gz && git add accounts.enc && git commit -m "Update cookies" && git push origin main', shell=True)
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(f"✅ {p_name} mis à jour ({len(clean)} cookies) et envoyé sur GitHub !".encode("utf-8"))
        elif self.path.startswith("/api/start"):
            with open("last_run.txt", "w") as f:
                f.write(str(time.time()))
            subprocess.run("git add auto_daily_bot.py .github/workflows/auto_9h_mensuel.yml last_run.txt && git commit -m 'Lancement Manuel: 63 posts x 20 commentaires (40s ecart)' && git push origin main", shell=True)
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write("✅ OPÉRATION LANCÉE ! Vos 63 publications reçoivent 20 commentaires chacune (écart 40s, Proxy Tunisien). Vous pouvez fermer votre Mac !".encode("utf-8"))

print("✅ APPLICATION PRÊTE : 63 PUBLICATIONS x 20 COMMENTAIRES (1 260 TOTAL) SUR LE PORT 8080 !")
HTTPServer(("0.0.0.0", 8080), AppHandler).serve_forever()
