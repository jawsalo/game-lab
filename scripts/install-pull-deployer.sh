#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 https://games.example.com" >&2
  exit 2
fi

base_url="${1%/}"
if [[ ! "$base_url" =~ ^https://[A-Za-z0-9.-]+(:[0-9]{1,5})?$ ]]; then
  echo "Base URL must be an HTTPS origin without a path." >&2
  exit 2
fi

if [[ "$EUID" -eq 0 ]]; then
  echo "Run this as the regular VPS operator account, not root." >&2
  exit 2
fi

deploy_repo="$HOME/game-lab-deployer"
venv="$HOME/.venvs/game-lab-pull-deploy"
unit_dir="$HOME/.config/systemd/user"
config_dir="$HOME/.config"

for command_name in git python3 kubectl helm systemctl; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "Required command not found: $command_name" >&2
    exit 1
  fi
done

kubectl -n game-lab get deployment/game-lab-api >/dev/null
helm -n game-lab status game-lab >/dev/null

if [[ -e "$deploy_repo" ]]; then
  if [[ ! -d "$deploy_repo/.git" ]]; then
    echo "Refusing to use a non-Git path: $deploy_repo" >&2
    exit 1
  fi
  origin="$(git -C "$deploy_repo" remote get-url origin)"
  if [[ "$origin" != "https://github.com/jawsalo/game-lab.git" && "$origin" != "git@github.com:jawsalo/game-lab.git" ]]; then
    echo "Unexpected origin for $deploy_repo: $origin" >&2
    exit 1
  fi
  if [[ -n "$(git -C "$deploy_repo" status --porcelain)" ]]; then
    echo "Refusing to update a dirty deployment checkout: $deploy_repo" >&2
    exit 1
  fi
  git -C "$deploy_repo" fetch --quiet origin main
  git -C "$deploy_repo" switch --quiet main
  git -C "$deploy_repo" pull --ff-only origin main
else
  git clone --branch main --single-branch https://github.com/jawsalo/game-lab.git "$deploy_repo"
fi

python3 -m venv "$venv"
"$venv/bin/python" -m pip install -r "$deploy_repo/requirements.txt" -r "$deploy_repo/apps/api/requirements.txt"

mkdir -p "$unit_dir" "$config_dir"
install -m 0644 "$deploy_repo/deploy/systemd/game-lab-pull-deploy.service" "$unit_dir/"
install -m 0644 "$deploy_repo/deploy/systemd/game-lab-pull-deploy.timer" "$unit_dir/"
umask 077
printf 'GAME_LAB_BASE_URL=%s\n' "$base_url" > "$config_dir/game-lab-pull-deploy.env"

sudo loginctl enable-linger "$USER"
systemctl --user daemon-reload
systemctl --user enable --now game-lab-pull-deploy.timer

cat <<EOF
Pull deployer installed. It will establish a no-deploy baseline on its first
successful check, then deploy later main-branch builds only after both image
publishing and full validation pass.

Check status:
  systemctl --user list-timers game-lab-pull-deploy.timer
  journalctl --user -u game-lab-pull-deploy.service -n 50 --no-pager

Disable automatic deployment:
  systemctl --user disable --now game-lab-pull-deploy.timer
EOF
