import time, urllib.request, subprocess, os, re

os.chdir("/workspaces/Fastlane")

def app_ok():
    try:
        urllib.request.urlopen("http://localhost:8099/api/list", timeout=5)
        return True
    except:
        return False

def cf_ok():
    res = subprocess.run(["pgrep", "-f", "cloudflared"], stdout=subprocess.PIPE)
    return res.returncode == 0

while True:
    if not app_ok():
        subprocess.Popen(["python3", "app.py"])
        time.sleep(3)
    if not cf_ok():
        subprocess.Popen(["./cloudflared", "tunnel", "--url", "http://localhost:8099"], stdout=open("tunnel.log", "w"), stderr=subprocess.STDOUT)
        time.sleep(5)
    try:
        log = open("tunnel.log").read()
        urls = re.findall(r'https://[-a-z0-9]*\.trycloudflare\.com', log)
        if urls:
            req = urllib.request.Request(urls[0] + "/api/list", headers={'User-Agent': 'Mozilla/5.0'})
            urllib.request.urlopen(req, timeout=10)
    except:
        pass
    time.sleep(45)
