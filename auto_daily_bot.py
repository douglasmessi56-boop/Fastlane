
def get_tn_proxy():
    import os, random, string, re
    s = os.environ.get("PROXY_TN", "").strip()
    if not s: return None
    if "://" in s and "@" in s:
        proto, rest = s.split("://", 1)
        creds, hp = rest.rsplit("@", 1)
        u, pw = creds.split(":", 1)
        base_pw = pw.split("_country-")[0]
        sid = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
        pw_clean = f"{base_pw}_country-tn_session-{sid}_lifetime-10m"
        return {"server": f"{proto}://{hp}", "username": u, "password": pw_clean}
    return {"server": s}

import os, sys, time, random, re
from datetime import datetime
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ACCOUNTS_DIR = os.path.join(BASE_DIR, "Comptes_FB_Fastlane")
DELAY_SECONDS = 40
MAX_COMMENTS_PER_POST = 20

POSTS_BY_CAT = {
    "SKIN": [
        "https://www.facebook.com/366848360837671/posts/1204914895092696",
        "https://www.facebook.com/366848360837671/posts/926495279601327",
        "https://www.facebook.com/366848360837671/posts/1299915252259326",
        "https://www.facebook.com/366848360837671/posts/726226652961525",
        "https://www.facebook.com/366848360837671/posts/1268545225396329",
        "https://www.facebook.com/366848360837671/posts/1242056758045176",
        "https://www.facebook.com/366848360837671/posts/1204914911759361",
        "https://www.facebook.com/366848360837671/posts/924546146462907"
    ],
    "MICOSE": [
        "https://www.facebook.com/366848360837671/posts/1242057008045151",
        "https://www.facebook.com/366848360837671/posts/715836170667240",
        "https://www.facebook.com/366848360837671/posts/1256827273234791",
        "https://www.facebook.com/366848360837671/posts/1299092455674939",
        "https://www.facebook.com/366848360837671/posts/1233121595605359",
        "https://www.facebook.com/366848360837671/posts/1242056664711852",
        "https://www.facebook.com/366848360837671/posts/1421545923429591",
        "https://www.facebook.com/366848360837671/posts/1256828453234673",
        "https://www.facebook.com/366848360837671/posts/803679928549530",
        "https://www.facebook.com/366848360837671/posts/1242055881378597",
        "https://www.facebook.com/366848360837671/posts/1242056254711893",
        "https://www.facebook.com/366848360837671/posts/716637470587110"
    ],
    "MINCY": [
        "https://www.facebook.com/366848360837671/posts/924627716454750",
        "https://www.facebook.com/366848360837671/posts/1242058051378380",
        "https://www.facebook.com/366848360837671/posts/1299602462290605",
        "https://www.facebook.com/366848360837671/posts/1258596416391210",
        "https://www.facebook.com/366848360837671/posts/1242055491378636",
        "https://www.facebook.com/366848360837671/posts/1258591116391740"
    ],
    "VARICES": [
        "https://www.facebook.com/366848360837671/posts/1258614553056063",
        "https://www.facebook.com/366848360837671/posts/1258610983056420",
        "https://www.facebook.com/366848360837671/posts/1258619333055585",
        "https://www.facebook.com/366848360837671/posts/1242057004711818",
        "https://www.facebook.com/366848360837671/posts/1269125648671620",
        "https://www.facebook.com/366848360837671/posts/1258601483057370",
        "https://www.facebook.com/366848360837671/posts/1258626089721576",
        "https://www.facebook.com/366848360837671/posts/680452527538938",
        "https://www.facebook.com/366848360837671/posts/716752447242279"
    ],
    "VITILIGHO": [
        "https://www.facebook.com/366848360837671/posts/1422873349963515",
        "https://www.facebook.com/366848360837671/posts/1424402539810596",
        "https://www.facebook.com/366848360837671/posts/1265706749013510",
        "https://www.facebook.com/366848360837671/posts/1266526742264844",
        "https://www.facebook.com/366848360837671/posts/1263690539215131",
        "https://www.facebook.com/366848360837671/posts/1263693572548161",
        "https://www.facebook.com/366848360837671/posts/1265703772347141",
        "https://www.facebook.com/366848360837671/posts/1266497185601133",
        "https://www.facebook.com/366848360837671/posts/1242058048045047",
        "https://www.facebook.com/366848360837671/posts/871908838393305"
    ],
    "EMMEROIDE": [
        "https://www.facebook.com/366848360837671/posts/891895566394632",
        "https://www.facebook.com/366848360837671/posts/739801321604058",
        "https://www.facebook.com/366848360837671/posts/1256146286636223",
        "https://www.facebook.com/366848360837671/posts/1421476300103220",
        "https://www.facebook.com/366848360837671/posts/1242057721378413",
        "https://www.facebook.com/366848360837671/posts/1424389729811877",
        "https://www.facebook.com/366848360837671/posts/1256148973302621",
        "https://www.facebook.com/366848360837671/posts/1242055481378637",
        "https://www.facebook.com/366848360837671/posts/1424401279810722"
    ],
    "ARTHROSE": [
        "https://www.facebook.com/366848360837671/posts/1263603292557189",
        "https://www.facebook.com/366848360837671/posts/1242056761378509",
        "https://www.facebook.com/366848360837671/posts/909269631323892",
        "https://www.facebook.com/366848360837671/posts/741345578116299",
        "https://www.facebook.com/366848360837671/posts/1421539030096947",
        "https://www.facebook.com/366848360837671/posts/1263599425890909",
        "https://www.facebook.com/366848360837671/posts/1263605752556943"
    ],
    "NEXORA": [
        "https://www.facebook.com/366848360837671/posts/1424477629803087",
        "https://www.facebook.com/366848360837671/posts/1424395183144665"
    ]
}

VILLES_AR = ["لتونس العاصمة", "لصفاقس", "لسوسة", "لبنزرت", "لنابل", "للقيروان", "لقابس", "لمدنين", "لمنستير", "لأريانة", "لبن عروس", "لجندوبة", "للكاف", "لقفصة"]
VILLES_FR = ["l Tounes", "l Sfax", "l Sousse", "l Bizerte", "l Nabeul", "l Monastir", "l Gabes", "l Ariana", "l Djerba", "l Kairouan", "l Mahdia", "l Beja"]

SUJETS_PAR_CAT = {
    "SKIN": {
        "ar_core": [
            "ينحي التجاعيد الصغيرة والخطوط الي بجنب العين",
            "يعطي نضارة للوجه ويرطب البشرة الجافة برشا",
            "يصلح للبشرة الحساسة وما يعملش حمار",
            "مكوناتو بالكولاجين وزبدة الشيا تخلي الوجه منور",
            "ينحي البقع الداكنة وآثار الحبوب القديمة",
            "يشد البشرة ويصفي الوجه من أول جمعة"
        ],
        "fr_core": [
            "yna7i les taches brunes w les rides sghar",
            "ykhali l wejh mnawwer w rtab barcha",
            "yosla7 lel peau sensible w ma yzayetch l wejh",
            "fih collagène naturel yched l barcha",
            "natijtou todhhor fisa3 3al wejh w l 3in",
            "y3awen barcha 3la ترطيب البشرة"
        ]
    },
    "MICOSE": {
        "ar_core": [
            "ينحي فطريات الضوافر نهائيا ويرجع الضفر نظيف",
            "يقضي على الحكّة والريحة الخايبة متاع الصبابط",
            "يرجع لون الضفر طبيعي بعد ما كان أصفر ومقشر",
            "يرتح الساقين من الفطريات بين الصوابع",
            "فعال برشا ضد الميكوز القديمة في الضوافر"
        ],
        "fr_core": [
            "yna7i mycose el dhwafer w yrajja3hom ndhaf",
            "yba3ed l 7akka w l fetryet mta3 sa9in",
            "mjarbou lel mycose mta3 dhfar l kbir tayara",
            "y3alej el dhwafer l m9achra fisa3",
            "natijtou madhmouna ضد فطريات الأظافر"
        ]
    },
    "MINCY": {
        "ar_core": [
            "يسد الشهية بالباهي ويعاون على حرق الدهون",
            "يطيح الكرش والجناب من غير تعب ولا دوخة",
            "ينقص الميزان بطريقة صحية ومكوناتو طبيعية",
            "يعاون برشا باش تنقص الحلاوي والماكلة في الليل",
            "يذوب الشحوم المتراكمة في الكرش بعد الولادة"
        ],
        "fr_core": [
            "y3awen barcha 3la تسكير الشهية وحرق الدهون",
            "yna9es l kerch w l jneb بلاش تعب",
            "tayacht bih 4 kilo fi chhar من غير حرمان",
            "طبيعي ما يقلقش المعدة جملة",
            "ykhallik tna9es fil mizen b saha"
        ]
    },
    "VARICES": {
        "ar_core": [
            "يرتح من الوجيعة والرزان متاع الساقين في الليل",
            "ينقص من بروز العروق الزرق والعنكبوتية في الساق",
            "يبرد الساقين وينحي النفخان بعد الوقوف الطويل",
            "يحسن الدورة الدموية في الساقين ويرتح الكعب",
            "يخفف السطر متاع الفاريس من أول دهنة"
        ],
        "fr_core": [
            "yrayah men وجيعة الساقين والعروق الزرق",
            "ybarred sa9in ba3d l 5edma w l we9fa",
            "yna9es el varices w el nafkhan fil k3ab",
            "khdhitou l ommi l9at 3lih ra7a kbira",
            "y5affef rzen sa9in fil lil barcha"
        ]
    },
    "VITILIGHO": {
        "ar_core": [
            "يرجع لون الجلدة الطبيعي للبقع البيضاء متاع البهاق",
            "يوحد لون البشرة في اليدين والوجه بشوية بشوية",
            "مكوناتو طبيعية تحفز الميلانين من غير حمار",
            "يغطي البلايص البيض ويرجعهم للون الجلدة",
            "يصلح للبهاق الخفيف والمتوسط ويعطي نتيجة باهية"
        ],
        "fr_core": [
            "yrajja3 loun el jelda el tabi3i lel vitiligo",
            "y3awen 3la توحيد لون البشرة والبقع البيضاء",
            "bdew el bo9a3 el bidh yerg3ou l lounhom",
            "yosla7 lel wejh w l ydin من غير حساسية",
            "طبيعي 100% ضد البهاق"
        ]
    },
    "EMMEROIDE": {
        "ar_core": [
            "يبرد السطر والحريق متاع البواسير من أول استعمال",
            "يرتح من النفخان والوجيعة في ظرف أيامات قليلة",
            "فعال برشا ضد الشرخ والبواسير الخارجية والداخلية",
            "يوقف الحكّة والقلق بمكونات طبيعية بالأعشاب",
            "رحمة كبيرة يرتحك في القعدة والمشي"
        ],
        "fr_core": [
            "yrayah men وجيعة البواسير والشرخ fisa3",
            "ybarred el 7ri9 w el nafkhan من أول نهار",
            "طبيعي بالأعشاب ما يعمل حتى قلق",
            "natijtou tayara ضد البواسير والحكّة",
            "رتحني بالحق بعد ما جربت برشا حاجات"
        ]
    },
    "ARTHROSE": {
        "ar_core": [
            "ينفع لوجيعة الركابي والظهر عند الكبار في العمر",
            "يرتح من الروماتيزم والخشونة في المفاصل",
            "يسخن البلاصة وينحي التصلب متاع الصباح",
            "ينحي سطر الرقبة والكتاف والمفاصل فيسع",
            "يعاون الوالدين باش يتحركو ويصليو براحتهم"
        ],
        "fr_core": [
            "yna7i وجيعة الركابي والمفاصل والظهر",
            "khdhitou lel weled 3la خاطر الروماتيزم ورتاح عليه",
            "ysa5en el mafasel w yna7i el sater fisa3",
            "tayara lel arthrose w خشونة الركبة",
            "men awwel jom3a t7es b far9 kbir fil 7araka"
        ]
    },
    "NEXORA": {
        "ar_core": [
            "منتج أصلي وفعال برشا والنتيجة متاعو مضمونة",
            "يعطي نتيجة سريعة ومن أول أسبوع تلاحظ الفرق",
            "مكوناتو طبيعية وجودة عالية برشا",
            "ننصح بيه الناس الكل خاطر بالحق يستاهل"
        ],
        "fr_core": [
            "produit original w natijtou todhhor fisa3",
            "mjarbou tayara barcha w qualité ممتازة",
            "يعطيكم الصحة على المصداقية والجودة",
            "men awwel jom3a l9it نتيجة روعة"
        ]
    }
}

def generate_unique_comment(cat, used_set):
    data = SUJETS_PAR_CAT.get(cat, SUJETS_PAR_CAT["SKIN"])
    for _ in range(100):
        style = random.choice(["ar_q", "ar_rev", "ar_cmd", "fr_q", "fr_rev", "fr_cmd"])
        v_ar = random.choice(VILLES_AR)
        v_fr = random.choice(VILLES_FR)
        c_ar = random.choice(data["ar_core"])
        c_fr = random.choice(data["fr_core"])

        if style == "ar_q":
            debut = random.choice(["بربي سؤال،", "سلام، بربي", "عسلامة، حبيت نسأل", "لو سمحتو،", "بربي جاوبوني،"])
            fin = random.choice([f"وقداش التوصيل {v_ar}؟", "والنتيجة بعد قداش تظهر؟", "والدفع عند الاستلام؟", "وفما تخفيض كي ناخذ زوج؟"])
            txt = f"{debut} هل بالحق {c_ar}؟ {fin}"
        elif style == "ar_rev":
            debut = random.choice(["والله عن تجربة", "الحمد لله خذيت منو،", "يعطيكم ألف صحة،", "بصراحة منتج روعة،", "جربتو عندي مدة،"])
            fin = random.choice(["ننصح بيه الناس الكل", "وصلتني الكوموند في يومين برك", "سلعة أصلية ومعاملة راقية", "رتحني برشا الحمد لله"])
            txt = f"{debut} {c_ar}، {fin}"
        elif style == "ar_cmd":
            debut = random.choice(["نحب نعدي كوموند", "بعثتلكم مساج في الخاص", "خليتلكم رقمي في البريفي", "حاجتي بعلبتين بربي"])
            txt = f"{debut} {v_ar}، ضاهر فيه {c_ar}، كلموني للتأكيد"
        elif style == "fr_q":
            debut = random.choice(["Slm brabi,", "3aslema,", "Brabi sou2el,", "Bjr,"])
            fin = random.choice([f"w b 9adeh livraison {v_fr} ?", "w 9adeh ya5ou wa9t el tawssil ?", "w fama promo 3la zouz 3lab ?"])
            txt = f"{debut} est-ce que {c_fr} ? {fin}"
        elif style == "fr_rev":
            debut = random.choice(["Mjarbou 3andi jom3tin,", "Wallahi tayara,", "Ya3tikom el sa7a,", "Saraha top,"])
            fin = random.choice(["livraison rapide l bab el dar", "nanssa7 bih 100%", "natija todhhor men awwel استعمـال"])
            txt = f"{debut} {c_fr} w {fin}"
        else:
            debut = random.choice(["Ena n7eb nsob commande", "B3atht numéro tel fil privé", "N7eb na5ou zouz", "Kallmouni nأكد الكوموند"])
            txt = f"{debut} {v_fr}, 3jabni khater {c_fr}"

        if txt not in used_set:
            used_set.add(txt)
            return txt
    return f"Slm n7eb n3adi commande {random.choice(VILLES_FR)}, b3atht fil privé"

def try_post_comment(page, comment):
    try:
        for sel in ['div[role="textbox"][contenteditable="true"]', 'div[aria-label*="omment"][contenteditable="true"]', 'div[aria-label*="تعليق"][contenteditable="true"]']:
            box = page.locator(sel).first
            if box.count() > 0 and box.is_visible():
                box.click(force=True)
                page.wait_for_timeout(900)
                page.keyboard.type(comment, delay=30)
                page.wait_for_timeout(800)
                page.keyboard.press("Enter")
                page.wait_for_timeout(3500)
                return True
    except:
        pass
    return False

def run_category(target_cat):
    profils = sorted([f for f in os.listdir(ACCOUNTS_DIR) if f.endswith(".json")])
    posts = POSTS_BY_CAT.get(target_cat, [])
    if not posts or not profils:
        print(f"⚠️ Rien à traiter pour {target_cat}")
        return

    print(f"============================================================")
    print(f"🚀 CATÉGORIE : {target_cat} | {len(posts)} Publications x {len(profils)} Profils")
    print(f"⏱️ Écart : {DELAY_SECONDS}s | Objectif : jusqu'à {MAX_COMMENTS_PER_POST} commentaires/post")
    print(f"============================================================")

    used_comments = set()
    post_counts = {u: 0 for u in posts}

    with sync_playwright() as p:
        for p_idx, prof in enumerate(profils):
            prof_path = os.path.join(ACCOUNTS_DIR, prof)
            print(f"\n👤 [{p_idx+1}/{len(profils)}] Test du profil : {prof} sur les {len(posts)} publications {target_cat}...")

            try:
                browser = p.chromium.launch(headless=True, proxy=get_tn_proxy(), args=["--no-sandbox", "--disable-blink-features=AutomationControlled"])
                context = browser.new_context(
                    storage_state=prof_path,
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                    viewport={"width": 1280, "height": 800}
                )
                page = context.new_page()

                for u_idx, target_url in enumerate(posts):
                    if post_counts[target_url] >= MAX_COMMENTS_PER_POST:
                        continue

                    comment = generate_unique_comment(target_cat, used_comments)
                    page.goto(target_url, wait_until="domcontentloaded", timeout=35000)
                    page.wait_for_timeout(4000)

                    if "checkpoint" in page.url or "login" in page.url:
                        print(f"🔴 {prof} : Checkpoint/Login détecté -> passage immédiat au profil suivant !")
                        break

                    ok = try_post_comment(page, comment)

                    if not ok:
                        mbasic_url = re.sub(r'^https?://(www\.|m\.)?facebook\.com', 'https://www.facebook.com', target_url)
                        page.goto(mbasic_url, wait_until="domcontentloaded", timeout=35000)
                        page.wait_for_timeout(3000)
                        if "checkpoint" in page.url or "login" in page.url:
                            print(f"🔴 {prof} : Checkpoint sur mbasic -> passage au profil suivant !")
                            break
                        print(f"   🌐 [{prof}] Titre: {page.title()[:35]} | URL: {page.url[:55]}")
                        posted_ok = False
                        for attempt_mode in ["desktop", "mobile"]:
                            if attempt_mode == "mobile":
                                m_url = page.url.replace("www.facebook.com", "m.facebook.com")
                                page.goto(m_url, wait_until="domcontentloaded", timeout=30000)
                                page.wait_for_timeout(3500)
                            # Fermer les popups cookies éventuels
                            for c_txt in ["Autoriser tous les cookies", "Allow all cookies", "السماح بكل ملفات تعريف الارتباط"]:
                                try:
                                    cb = page.locator(f"text='{c_txt}'").first
                                    if cb.is_visible(timeout=400): cb.click(); page.wait_for_timeout(800)
                                except: pass
                            # Scroller et cliquer sur le bouton Commenter / تعليق pour déplier la zone
                            page.mouse.wheel(0, 400)
                            page.wait_for_timeout(1200)
                            for btn_sel in ["div[role='button']:has-text('Commenter')", "div[role='button']:has-text('تعليق')", "span:has-text('Commenter')", "span:has-text('تعليق')", "[aria-label*='omment' i]", "[aria-label*='تعليق']"]:
                                try:
                                    b_el = page.locator(btn_sel).first
                                    if b_el.is_visible(timeout=600):
                                        b_el.click(force=True)
                                        page.wait_for_timeout(1500)
                                        break
                                except: pass
                            # Chercher la zone de texte
                            ta = page.locator('div[role="textbox"][contenteditable="true"], div[contenteditable="true"][aria-label*="omment" i], div[contenteditable="true"][aria-label*="تعليق"], div[contenteditable="true"][aria-label*="اكتب"], div[contenteditable="true"], textarea[name="comment_text"], textarea').last
                            if ta.is_visible(timeout=3500):
                                ta.scroll_into_view_if_needed()
                                ta.click(force=True)
                                page.wait_for_timeout(700)
                                msg = random.choice(COMMENTS)
                                page.keyboard.type(msg, delay=35)
                                page.wait_for_timeout(800)
                                page.keyboard.press("Enter")
                                page.wait_for_timeout(2500)
                                for s_btn in ["[aria-label='Commenter']", "[aria-label='تعليق']", "[aria-label='Envoyer']", "[aria-label='إرسال']", "button[type='submit']"]:
                                    try:
                                        sb = page.locator(s_btn).last
                                        if sb.is_visible(timeout=500): sb.click(force=True); page.wait_for_timeout(1200); break
                                    except: pass
                                print(f"   ✅ {prof} : Commentaire publié sur Post {u_idx+1} ({attempt_mode}) -> {msg}")
                                posted_ok = True
                                break
                        if not posted_ok:
                            print(f"   ⚠️ {prof} : Zone commentaire non trouvée sur Post {u_idx+1}")

                browser.close()
            except Exception as e:
                print(f"❌ Erreur sur {prof} : {e}")

if __name__ == "__main__":
    cat_arg = sys.argv[1] if len(sys.argv) > 1 else "ALL"
    if cat_arg == "ALL":
        for c in POSTS_BY_CAT.keys():
            run_category(c)
    else:
        run_category(cat_arg)
