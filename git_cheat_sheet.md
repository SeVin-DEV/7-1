# Git Cheat Sheet 🐙

Quick reference for managing your project from the terminal.

## 1. Initial Setup
```bash
# Set your identity (one-time)
git config --global user.name "Your Name"
git config --global user.email "youremail@example.com"

# Clone the repo
git clone https://github.com/SeVin-DEV/7-1.git
cd 7-1
```

## 2. Basic Workflow (Pushing Changes)
```bash
# 1. Switch to the branch you want to work on
git checkout master

# 2. Stage specific files you've changed
git add path/to/your/file.txt
# OR stage everything: git add .

# 3. Commit with a message
git commit -m "Describe what you changed"

# 4. Push to the specific branch
git push origin master
```

## 3. Managing Branches
```bash
# List all branches
git branch -a

# Switch to main branch
git checkout main

# Create and switch to a new branch
git checkout -b new-branch-name

# Merge master into main
git checkout main
git merge master
```

## 4. Updates and Cleanup
```bash
# Pull latest changes from GitHub
git pull origin master

# Remove a file from GitHub but keep it locally
git rm --cached filename

# Check what's going on (which files are staged/changed)
git status
```

## 5. .gitignore
Create a file named `.gitignore` in the root folder to list files Git should ignore (like `node_modules/`, `.DS_Store`, or large zip files).
