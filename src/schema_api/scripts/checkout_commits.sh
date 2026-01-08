#!/bin/bash
set -e

# Load the 2 commits to compare from the command line
base_commit=$1
update_commit=$2
tmp_dir=$3

# Checkout and save the repo for the 2 commits
cd $tmp_dir/amsterdam-schema
mkdir ../changes/${base_commit}
mkdir ../changes/${update_commit}

git archive "$base_commit" | tar -x -C "../changes/${base_commit}"
git archive "$update_commit" | tar -x -C "../changes/${update_commit}"

# Return the date on which the update commit was merged (format-local means in timezone of current user)
date=$(git show -s --date=format-local:'%Y-%m-%d %H:%M:%S' --no-patch --format=%cd $update_commit)
echo "$date"
