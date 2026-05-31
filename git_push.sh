#!/usr/bin/env zsh
# push.sh — sync local changes to GitHub with safety checks

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
REMOTE="origin"
BRANCH="main"

cd "$REPO_DIR"

echo "==> Repo: $REPO_DIR"
echo "==> Branch: $BRANCH | Remote: $REMOTE"
echo ""

# 1. Перевірка наявності змін
if git diff --quiet && git diff --cached --quiet; then
  echo "[INFO] No local changes detected."
  git status
  exit 0
fi

# 2. Список змінених файлів
echo "==> Changed files:"
git status --short
echo ""

# 3. Fetch remote — перевірка розбіжностей
echo "==> Fetching remote..."
git fetch "$REMOTE" "$BRANCH"

LOCAL=$(git rev-parse HEAD)
REMOTE_SHA=$(git rev-parse "$REMOTE/$BRANCH")
BASE=$(git merge-base HEAD "$REMOTE/$BRANCH")

if [ "$LOCAL" != "$BASE" ] && [ "$REMOTE_SHA" != "$BASE" ]; then
  echo "[ERROR] Diverged histories. Manual merge required."
  echo "  Local:  $LOCAL"
  echo "  Remote: $REMOTE_SHA"
  exit 1
fi

if [ "$REMOTE_SHA" != "$BASE" ]; then
  echo "==> Remote has new commits. Pulling with rebase..."
  git pull --rebase "$REMOTE" "$BRANCH"
fi

# 4. Stage all changes
git add -A

# 5. Commit message — з аргументу або інтерактивно
if [ -n "${1:-}" ]; then
  MSG="$1"
else
  printf "Commit message: "
  read -r MSG
fi

if [ -z "$MSG" ]; then
  echo "[ERROR] Commit message cannot be empty."
  exit 1
fi

git commit -m "$MSG"

# 6. Push
echo "==> Pushing to $REMOTE/$BRANCH..."
git push "$REMOTE" "$BRANCH"

echo ""
echo "[OK] Done."
git log --oneline -5
