#!/usr/bin/env bash
# Fail if any personal identifier or secret shape appears in tracked files.
# Run before every push:  bash scripts/redact-check.sh
#
# The repo owner's GitHub handle is the ONE allowed identity token, because it
# appears in the clone URL. Everything else must be absent.

set -uo pipefail
cd "$(dirname "$0")/.." || exit 1

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[0;33m'; NC='\033[0m'

# Personal identifiers — case-insensitive
PII='nilabh yadav|agrobothex|@gmail\.com|users[/\\]nilab\b|tailscale|ts\.net|192\.168\.|[0-9]{2}:[0-9]{2}:[0-9]{2}:[0-9]{2}|@nilabh'

# Secret shapes
SECRETS='ghp_[A-Za-z0-9]{20,}|gho_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}|AIza[0-9A-Za-z_-]{30,}|-----BEGIN [A-Z ]*PRIVATE KEY-----'

scan() {
  local label="$1" pattern="$2" hits
  hits=$(grep -rInE -i \
      --exclude-dir=.git \
      --exclude-dir=__pycache__ \
      --exclude='redact-check.sh' \
      "$pattern" . 2>/dev/null)
  if [ -n "$hits" ]; then
    printf "%b\n" "${RED}FAIL${NC} — $label"
    printf '%s\n' "$hits" | sed 's/^/    /'
    return 1
  fi
  printf "%b\n" "${GREEN}ok${NC}   — no $label"
  return 0
}

status=0
scan "personal identifiers" "$PII" || status=1
scan "secret-shaped strings" "$SECRETS" || status=1

# Files that must never be committed
for f in LOCAL.md .env SOUL.md.bak; do
  if find . -path ./.git -prune -o -name "$f" -print 2>/dev/null | grep -q .; then
    printf "%b\n" "${YELLOW}WARN${NC} — $f present in the working tree (must be gitignored, never committed)"
  fi
done

if [ "$status" -ne 0 ]; then
  printf "\n%b\n" "${RED}Redaction check FAILED — do not push.${NC}"
  exit 1
fi
printf "\n%b\n" "${GREEN}Redaction check clean.${NC}"
