#!/usr/bin/env bash
set -euo pipefail

REPO_NAME="${1:-sim-swap-otp-lab}"
OWNER="${2:-burnt-exe}"
VISIBILITY="${3:-private}"

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI 'gh' is required. Install it from https://cli.github.com/ and run 'gh auth login'." >&2
  exit 1
fi

if [[ "$VISIBILITY" != "private" && "$VISIBILITY" != "public" ]]; then
  echo "Visibility must be 'private' or 'public'." >&2
  exit 1
fi

git init

git add .
git commit -m "Initial SIM Swap OTP Lab"

gh repo create "$OWNER/$REPO_NAME" --"$VISIBILITY" --source=. --remote=origin --push

echo "Repository created: https://github.com/$OWNER/$REPO_NAME"
