#!/usr/bin/env zsh
set -e
MSG="${1:-Update dashboard data}"
git add .
if git diff --cached --quiet; then
  echo "Nothing to commit"
else
  git commit -m "$MSG"
fi
git pull --rebase origin main
git push origin main
