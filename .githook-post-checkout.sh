#/bin/sh
#mv .githook-post-checkout.sh .git/hooks/post-checkout
echo "[post-checkout hook: $1]"

changed_files="$(git diff-tree -r --name-only --no-commit-id ORIG_HEAD HEAD)"

check_run() {
  echo "$changed_files" | grep -E --quiet "$1" && eval "$2"
}

check_run website/static/package.json "(cd website/static; npm update)"
check_run requirements.txt "(source env/bin/activate; pip install -r requirements.txt)"
check_run static "(source env/bin/activate; python3.6 manage.py collectstatic --clear)"

exit 0 #Needed so Visual Studio Code does not display an error
