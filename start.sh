#!/bin/bash
 # --- KAYDEN SYSTEM BOOTLOADER (ORCHESTRATOR v8.2 FINAL) ---
 
 set -e
 
 trap "echo -e '\n[KAYDEN] Shutdown signal received. Exiting cleanly.'; exit 0" SIGINT SIGTERM
 
 
 # =========================
 # 🧠 GIT STATE CHECK
 # =========================
 
 check_git_state() {
     git fetch origin >/dev/null 2>&1
 
     LOCAL=$(git rev-parse @)
     REMOTE=$(git rev-parse origin/main)
     BASE=$(git merge-base @ origin/main)
 
     if [ "$LOCAL" = "$REMOTE" ]; then
         echo "CLEAN"
     elif [ "$LOCAL" = "$BASE" ]; then
         echo "BEHIND"
     elif [ "$REMOTE" = "$BASE" ]; then
         echo "AHEAD"
     else
         echo "DIVERGED"
     fi
 }
 
 
 handle_git_sync() {
     STATE=$(check_git_state)
 
     echo "[KAYDEN] Git state: $STATE"
 
     if [ "$STATE" = "CLEAN" ]; then
         return
     fi
 
     echo "[KAYDEN] Sync options:"
     echo "1) Pull"
     echo "2) Push"
     echo "3) Skip"
 
     read -t 10 -p "Choice (auto-skip in 10s): " choice || choice="3"
 
     case $choice in
         1)
             git pull origin main --no-rebase || echo "[WARN] Pull conflict"
             ;;
         2)
             git push origin main || echo "[WARN] Push failed"
             ;;
         *)
             echo "[KAYDEN] Skipping git sync"
             ;;
     esac
 }
 
 
 # =========================
 # 🔌 PNP SCANNER
 # =========================
 
 scan_plugins() {
     echo "[KAYDEN] Scanning system buses..."
 
     PATCH_LIST=$(ls patches/*.py 2>/dev/null | grep -v "patches_bridge.py" | xargs -n 1 basename | sed 's/\.py//' | tr '\n' ',' | sed 's/,$//')
     TOOL_LIST=$(ls tools/*.py 2>/dev/null | grep -v "tools_bridge.py" | xargs -n 1 basename | sed 's/\.py//' | tr '\n' ',' | sed 's/,$//')
 
     if [ ! -f "patches/patches_bridge.py" ] || [ ! -f "tools/tools_bridge.py" ]; then
         echo "[CRITICAL] Bridge controllers missing"
         exit 1
     fi
 
     export SVN_ACTIVE_PATCHES=$PATCH_LIST
     export SVN_ACTIVE_TOOLS=$TOOL_LIST
 
     echo "[KAYDEN] Tools: ${TOOL_LIST:-None}"
     echo "[KAYDEN] Patches: ${PATCH_LIST:-None}"
 }
 
 
 # =========================
 # 🚀 SERVER BOOT (CRITICAL CORE)
 # =========================
 
 boot_server() {
     echo "[KAYDEN] ------------------------------------"
     echo "[KAYDEN] Starting FastAPI Kernel"
     echo "[KAYDEN] Binding: http://0.0.0.0:8080"
     echo "[KAYDEN] System Runtime: ONLINE"
     echo "[KAYDEN] ------------------------------------"
 
     uvicorn main:app --host 0.0.0.0 --port 8080
 }
 
 
 # =========================
 # 💾 MEMORY VAULT
 # =========================
 
 vault_memory() {
     echo "[KAYDEN] Saving memory state..."
 
     git checkout main
 
     git add identity/*.md state/*.json state/notes/* 2>/dev/null || true
 
     if ! git diff-index --quiet HEAD --; then
         git commit -m "KAYDEN: Memory Sync $(date)"
         git push origin main
     fi
 }
 
 
 # =========================
 # 🧪 CODE VAULT
 # =========================
 
 vault_code() {
     echo "[KAYDEN] Saving staging snapshot..."
 
     git checkout staging
     git add .
 
     if ! git diff-index --quiet HEAD --; then
         git commit -m "KAYDEN: Code Snapshot $(date)"
         git push origin staging
     fi
 
     git checkout main
 }
 
 
 # =========================
 # 🔁 SYSTEM LOOP
 # =========================
 
 while true; do
 
     echo "[KAYDEN] === NEW BOOT CYCLE ==="
 
     scan_plugins
     handle_git_sync
 
     boot_server
 
     echo "[KAYDEN] Server stopped or crashed."
 
     vault_memory
     vault_code
 
     echo "[KAYDEN] Restarting in 5 seconds..."
     sleep 5
 
 done
