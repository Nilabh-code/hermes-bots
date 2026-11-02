#!/usr/bin/env python3
"""Install the hermes-bots crew into a local Hermes Agent installation.

Each bot is a Hermes *profile*. This script creates the profile (optionally
cloning your active profile's config and API keys), then drops the bot's
SOUL.md and profile.yaml into place.

Usage:
    python install.py                       # all bots
    python install.py --bots orchestrator,reviewer
    python install.py --dry-run
    python install.py --no-clone            # empty profile, no inherited keys
    python install.py --model Deepseek-v4.1-Flash --provider custom
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
BOTS_DIR = REPO / "bots"
LOCAL_EXAMPLE = REPO / "docs" / "LOCAL.md.example"


def hermes_home() -> Path:
    env = os.environ.get("HERMES_HOME")
    if env:
        return Path(env).expanduser()
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA") or (Path.home() / "AppData" / "Local"))
        return base / "hermes"
    return Path.home() / ".hermes"


def hermes_bin() -> str | None:
    for name in ("hermes", "hermes.cmd", "hermes.bat", "hermes.exe"):
        found = shutil.which(name)
        if found:
            return found
    return None


def read_description(profile_yaml: Path) -> str:
    """Pull the top-level `description:` value, folding YAML line continuations."""
    text = profile_yaml.read_text(encoding="utf-8")
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("description:"):
            value = line.split(":", 1)[1].strip()
            j = i + 1
            while j < len(lines) and lines[j].startswith(("  ", "\t")) and not lines[j].strip().startswith(("color:", "shape:")):
                value += " " + lines[j].strip()
                j += 1
            return value.strip().strip("'\"")
    return ""


def run(cmd: list[str], dry_run: bool) -> tuple[int, str]:
    printable = " ".join(cmd)
    if dry_run:
        print(f"    would run: {printable}")
        return 0, ""
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, str(exc)
    out = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, out.strip()


def available_bots() -> list[str]:
    if not BOTS_DIR.is_dir():
        return []
    return sorted(p.name for p in BOTS_DIR.iterdir() if (p / "SOUL.md").is_file())


def install_bot(name: str, home: Path, args, hermes: str | None) -> bool:
    src = BOTS_DIR / name
    soul_src = src / "SOUL.md"
    yaml_src = src / "profile.yaml"
    if not soul_src.is_file():
        print(f"  [{name}] SKIP — no SOUL.md in {src}")
        return False

    dest = home / "profiles" / name
    print(f"  [{name}] profile dir: {dest}")

    if not dest.exists():
        if not hermes:
            print("  [error] `hermes` not found on PATH — install Hermes first:")
            print("          curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash")
            return False
        cmd = [hermes, "profile", "create", name]
        if not args.no_clone:
            cmd.append("--clone")
        desc = read_description(yaml_src)
        if desc:
            cmd += ["--description", desc]
        code, out = run(cmd, args.dry_run)
        if code != 0:
            print(f"  [error] profile create failed ({code}):\n{out}")
            return False
        if out:
            print("    " + out.replace("\n", "\n    "))

    if args.dry_run:
        print(f"    would copy SOUL.md -> {dest / 'SOUL.md'}")
        print(f"    would copy profile.yaml -> {dest / 'profile.yaml'}")
        return True

    dest.mkdir(parents=True, exist_ok=True)

    soul_dest = dest / "SOUL.md"
    if soul_dest.exists():
        backup = dest / "SOUL.md.bak"
        shutil.copy2(soul_dest, backup)
        print(f"    backed up existing SOUL.md -> {backup.name}")
    shutil.copy2(soul_src, soul_dest)
    print(f"    SOUL.md installed ({soul_dest.stat().st_size} bytes)")

    shutil.copy2(yaml_src, dest / "profile.yaml")
    print("    profile.yaml installed (roster name, colour, avatar)")

    local_dest = dest / "LOCAL.md"
    if not local_dest.exists() and LOCAL_EXAMPLE.is_file():
        shutil.copy2(LOCAL_EXAMPLE, local_dest)
        print("    LOCAL.md created from template — EDIT IT with your own facts")

    if args.model:
        if not hermes:
            print("    [warn] no `hermes` on PATH — model not pinned")
        else:
            if args.provider:
                code, out = run([hermes, "-p", name, "config", "set", "model.provider", args.provider], False)
                if code != 0:
                    print(f"    [warn] provider set failed: {out}")
            code, out = run([hermes, "-p", name, "config", "set", "model.default", args.model], False)
            print(f"    model pinned -> {args.model}" if code == 0 else f"    [warn] model set failed: {out}")

    return True


def main() -> int:
    ap = argparse.ArgumentParser(description="Install the hermes-bots crew.")
    ap.add_argument("--bots", default="all", help="comma-separated bot names, or 'all'")
    ap.add_argument("--model", help="pin this model id for every installed bot")
    ap.add_argument("--provider", help="pin this provider (used with --model)")
    ap.add_argument("--no-clone", action="store_true", help="do not inherit config/keys from the active profile")
    ap.add_argument("--dry-run", action="store_true", help="print actions, change nothing")
    args = ap.parse_args()

    home = hermes_home()
    hermes = hermes_bin()
    all_bots = available_bots()
    if not all_bots:
        print(f"No bots found under {BOTS_DIR}")
        return 2

    if args.bots.strip().lower() == "all":
        wanted = all_bots
    else:
        wanted = [b.strip() for b in args.bots.split(",") if b.strip()]
        unknown = [b for b in wanted if b not in all_bots]
        if unknown:
            print(f"Unknown bot(s): {', '.join(unknown)}. Available: {', '.join(all_bots)}")
            return 2

    print(f"Hermes home : {home}")
    print(f"hermes CLI  : {hermes or 'NOT FOUND (only existing profiles can be updated)'}")
    print(f"Bots        : {', '.join(wanted)}")
    print(f"Mode        : {'DRY RUN' if args.dry_run else 'INSTALL'}\n")

    ok, failed = [], []
    for name in wanted:
        (ok if install_bot(name, home, args, hermes) else failed).append(name)
        print()

    print(f"Installed: {len(ok)}/{len(wanted)}" + (f"  failed: {', '.join(failed)}" if failed else ""))
    if not args.dry_run and ok:
        print("\nNext:")
        print(f"  1. Fill in operator facts: {home / 'profiles' / ok[0] / 'LOCAL.md'}")
        print("  2. Smoke test:  hermes -p orchestrator chat -q \"Reply with your name and one sentence on what you do. No tools.\"")
        print("  3. Open the Bots tab — the crew is in the roster.")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
