#!/usr/bin/env python3
import subprocess
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

REPO_URL = os.getenv("REPO_URL")
PAT = os.getenv("GITHUB_PAT")

def run_git_command(cmd, check=True):
    print(f"🧪 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip())
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}")

def setup_auth():
    if not PAT or not REPO_URL:
        raise ValueError("Missing GITHUB_PAT or REPO_URL in .env")

    # Replace https:// with PAT injection
    authed_url = REPO_URL.replace("https://", f"https://{PAT}@")
    run_git_command(f"git remote set-url origin {authed_url}")

def push_changes():
    run_git_command("git add data/*.json docs/*.html archive/*.zip", check=False)
    run_git_command('git commit -m "📡 New diagnostics and plots" || echo "No changes to commit"', check=False)
    run_git_command("git push origin main")

def main():
    setup_auth()
    push_changes()

if __name__ == "__main__":
    main()
