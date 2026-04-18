#!/bin/bash
 # --- SYSTEM INSTALLER (MANIFEST-DRIVEN v2.0) ---
 
 set -e
 
 echo "[INSTALL] Booting system installer..."
 
 # =========================
 # 📦 SYSTEM CHECK
 # =========================
 
 command -v python3 >/dev/null 2>&1 || { echo "[ERROR] python3 missing"; exit 1; }
 command -v pip >/dev/null 2>&1 || { echo "[ERROR] pip missing"; exit 1; }
 command -v git >/dev/null 2>&1 || { echo "[ERROR] git missing"; exit 1; }
 
 echo "[INSTALL] Base dependencies verified."
 
 
 # =========================
 # 📄 DEPENDENCY INSTALLER
 # =========================
 
 REQ_FILE="requirements.txt"
 
 if [ ! -f "$REQ_FILE" ]; then
     echo "[ERROR] Missing $REQ_FILE"
     exit 1
 fi
 
 echo "[INSTALL] Installing Python dependencies..."
 
 while read -r package || [ -n "$package" ]; do
     # Skip empty lines or comments
     if [[ -z "$package" || "$package" == \#* ]]; then
         continue
     fi
 
     echo "[INSTALL] Installing $package..."
     pip install "$package"
 
 done < "$REQ_FILE"
 
 echo "[INSTALL] Python dependencies installed."
 
 
 # =========================
 # 🌱 ENV WIZARD
 # =========================
 
 echo "[INSTALL] Creating environment config..."
 
 read -p "API_KEY (or 'none'): " API_KEY
 read -p "API_BASE_URL (default http://localhost:1234/v1): " API_BASE_URL
 read -p "MODEL_NAME: " MODEL_NAME
 
 API_BASE_URL=${API_BASE_URL:-http://localhost:1234/v1}
 
 cat > .env <<EOL
 API_KEY=$API_KEY
 API_BASE_URL=$API_BASE_URL
 MODEL_NAME=$MODEL_NAME
EOL
 
 echo "[INSTALL] .env created."
 
 
 # =========================
 # 🔐 GIT CONFIG
 # =========================
 
 echo "[INSTALL] Configuring git identity..."
 
 read -p "Git username: " GIT_NAME
 read -p "Git email: " GIT_EMAIL
 
 git config --global user.name "$GIT_NAME"
 git config --global user.email "$GIT_EMAIL"
 
 echo "[INSTALL] Git configured."
 
 
 # =========================
 # 🧹 GITIGNORE SAFETY
 # =========================
 
 cat > .gitignore <<EOL
 .env
 __pycache__/
 *.pyc
 state/
 logs/
 *.log
EOL
 
 echo "[INSTALL] .gitignore applied."
 
 
 # =========================
 # 🌐 REPO INIT
 # =========================
 
 if [ ! -d ".git" ]; then
     git init
 fi
 
 read -p "Remote origin URL (optional): " REMOTE_URL
 
 if [ ! -z "$REMOTE_URL" ]; then
     git remote remove origin 2>/dev/null || true
     git remote add origin "$REMOTE_URL"
 fi
 
 
 # =========================
 # 🔍 STRUCTURE VALIDATION
 # =========================
 
 echo "[INSTALL] Validating system structure..."
 
 FILES=(
     "main.py"
     "start.sh"
     "core/engine.py"
     "tools/tools_bridge.py"
     "patches/patches_bridge.py"
 )
 
 for f in "${FILES[@]}"; do
     if [ ! -f "$f" ]; then
         echo "[ERROR] Missing file: $f"
         exit 1
     fi
 done
 
 echo "[INSTALL] System validated."
 
 
 # =========================
 # 🚀 DONE
 # =========================
 
 echo ""
 echo "[INSTALL COMPLETE]"
 echo "Run system with: ./start.sh"
 echo ""
