#!/bin/bash
set -e
# Clone Amsterdam Schema repo

start_commit=$1
end_commit=$2
tmp_dir=$3
echo "Generating changelog updates from commit:"
echo $start_commit
echo "to commit:"
echo $end_commit

cd $tmp_dir
mkdir changes
echo "Cloning Amsterdam Schema repo..."
git clone https://github.com/Amsterdam/amsterdam-schema.git
cd amsterdam-schema
git config pull.ff only
echo "Done!"

# Fetch history of commits into master (oldest to newest)
git pull
git fetch origin master

# First fetch all commits from start commit to head (we get the reverse order)
commits=$(git log $start_commit^..HEAD --first-parent master --pretty=format:"%H")

# Only save commits between start and end (if end commit is specified)
flag="False"

new_to_old_commits=()
for commit in $commits; do
    if [[ "$commit" == "$end_commit" ]]; then
        flag=True
    fi
    if [[ "$flag" == "True" ]] || [[ "$end_commit" == "HEAD" ]]; then
        new_to_old_commits+=("$commit")
    fi
done

# Reverse the array
old_to_new_commits=()
for ((i=${#new_to_old_commits[@]}-1; i>=0; i--)); do
    old_to_new_commits+=("${new_to_old_commits[i]}")
done

# Save the array
printf "%s\n" "${old_to_new_commits[@]}" > ../commits.txt
