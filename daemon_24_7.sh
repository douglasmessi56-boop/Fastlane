#!/bin/bash
cd /workspaces/Fastlane

while true; do
  # 1. Empêcher GitHub Codespaces de dormir (simule une activité système + écriture disque)
  date > /tmp/.codespace_heartbeat
  touch /workspaces/Fastlane/.keepalive

  # 2. Vérifier et relancer app.py s'il est arrêté
  if ! pgrep -f "python3 /workspaces/Fastlane/app.py" > /dev/null; then
    nohup python3 /workspaces/Fastlane/app.py > /workspaces/Fastlane/app.log 2>&1 &
  fi

  # 3. Vérifier et relancer cloudflared s'il est arrêté
  if ! pgrep -f "cloudflared tunnel" > /dev/null; then
    rm -f /workspaces/Fastlane/tunnel.log
    nohup /workspaces/Fastlane/cloudflared tunnel --url http://localhost:8099 > /workspaces/Fastlane/tunnel.log 2>&1 &
  fi

  sleep 60
done
