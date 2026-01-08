#!/bin/bash
set -e

# Load update commit and tmp folder
update_commit=$1
tmp_dir=$2

# Checkout and save the repo for the update commit
cd $tmp_dir/amsterdam-schema
mkdir ../changes/${update_commit}

git archive "$update_commit" | tar -x -C "../changes/${update_commit}"

# Return the date on which the update commit was merged (format-local means in timezone of current user)
date=$(git show -s --date=format-local:'%Y-%m-%d %H:%M:%S' --no-patch --format=%cd $update_commit)
echo "$date"
