#!/bin/bash
# Clone Amsterdam Schema repo

start_commit=$1
end_commit=$2
echo "Generating Changelog update from commit:"
echo $start_commit
echo "to commit:"
echo $end_commit

mkdir tmp
cd tmp
mkdir changes
echo "Cloning Amsterdam Schema repo..."
git clone git@github.com:Amsterdam/amsterdam-schema.git
echo "Done!"


# Fetch history of commits into master (oldest to newest)
cd amsterdam-schema
git pull
git fetch origin master

# First fetch all commits from start commit to head
commits=$(git log $start_commit^..HEAD --first-parent master --pretty=format:"%H")

# Only save commits between start and end (if end commit is specified)
flag="False"

original_array=()
for commit in $commits; do
    if [[ "$commit" == "$end_commit" ]]; then
        flag=True
    fi
    if [[ "$flag" == "True" ]] || [[ "$end_commit" == "HEAD" ]]; then
        original_array+=("$commit")
    fi
done

# Reverse the array
reversed_commits=()
for ((i=${#original_array[@]}-1; i>=0; i--)); do
    reversed_commits+=("${original_array[i]}")
done

# Save the array
printf "%s\n" "${reversed_commits[@]}" > ../commits.txt
