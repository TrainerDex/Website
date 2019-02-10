#/bin/bash
#cp .githook-post-checkout.sh .git/hooks/post-checkout
echo "[post-checkout hook: $1]"

changed_files="$(git diff-tree -r --name-only --no-commit-id ORIG_HEAD HEAD)"

check_run() {
  echo "$changed_files" | grep -E "$1" && eval "$2"
}

check_run "core/static/package.json" "(echo -e '\033[0;31mnode_modules changed\e[0m'; cd website/static; npm update --verbose)"
check_run "requirements.txt" "(echo -e '\033[0;31mpython requirements.txt changed\e[0m'; source env/bin/activate; pip install -r requirements.txt)"
check_run "(static)|(requirements.txt)" "(echo -e '\033[0;31mstatic files changed\e[0m'; source env/bin/activate; python manage.py collectstatic --clear --noinput)"

exit 0
