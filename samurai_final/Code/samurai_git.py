#!/usr/bin/env python3
# samurai_git.py — Smart Git Bypass
import subprocess, pathlib, json, datetime, sys

BASE = pathlib.Path(__file__).resolve().parent.parent

def run(cmd, shell=True):
    print(f"⚡ {cmd}")
    return subprocess.run(cmd, shell=shell)

def init_smart():
    run("git init")
    run('git config user.name "Nishan Ramanathan"')
    run('git config user.email "nishan@xtobe.com"')
    gitignore = BASE / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("__pycache__/\n*.pyc\n*.png\nExports/\nprojects/*/Gen/\n.env\nvenv/\n")
    print("✓ init-smart done")

def commit_smart(msg=None):
    run("git add.")
    if not msg:
        result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
        changed = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
        msg = f"auto-sync: {changed} files — {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} — samurai v1.1 shadow"
    run(f'git commit -m "{msg}"')
    manifest = BASE / "manifest.json"
    if manifest.exists():
        data = json.loads(manifest.read_text())
        data["last_sync"] = datetime.datetime.now().isoformat()
        manifest.write_text(json.dumps(data, indent=2))
    print("✓ commit-smart done")

def push_smart():
    run("git push -u origin main")
    run("git push origin --tags")
    print("✓ push-smart done")

def tag_smart(tag):
    run(f'git tag -a {tag} -m "Samurai {tag} — shadow release"')
    run(f"git push origin {tag}")
    print(f"✓ tag-smart {tag} done")

def sync():
    commit_smart()
    push_smart()

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "sync"
    if cmd == "init-smart": init_smart()
    elif cmd.startswith("commit"): commit_smart(" ".join(sys.argv[2:]) if len(sys.argv) > 2 else None)
    elif cmd == "push-smart": push_smart()
    elif cmd.startswith("tag"): tag_smart(sys.argv[2] if len(sys.argv) > 2 else "v1.1.0-shadow")
    else: sync()