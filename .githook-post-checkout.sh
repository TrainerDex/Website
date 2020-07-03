#/bin/bash
echo "[post-checkout hook: $1]"

file1=".githook-post-checkout.sh"
file2=".git/hooks/post-checkout"

printf "Checking for changes to '$file1'"
if cmp -s "$file1" "$file2"; then
    # Clear line
    printf "\r\033[K"
else
    printf "\r\033[KChanges found... copying '$file1' to '$file2'\n"
    cp "$file1" "$file2"
    printf "Restarting script\n"
    sh "$file2"
    exit 0
fi


changed_files="$(git diff-tree -r --name-only --no-commit-id ORIG_HEAD HEAD)"

check_run() {
  echo "$changed_files" | grep -E "$1" && eval "$2"
}

check_run "requirements.txt" "(echo -e '\033[0;31mpython requirements.txt changed\e[0m'; source backend/env/bin/activate; pip install -r backend/requirements.txt)"
check_run "(static)|(requirements.txt)" "(echo -e '\033[0;31mstatic files changed\e[0m'; source backend/env/bin/activate; python backend/manage.py collectstatic --clear --noinput)"

exit 0
