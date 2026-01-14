#!/bin/bash
set -e

# Load update commit and tmp folder
commit=$1
tmp_dir=$2

# Checkout and save the repo for the update commit
cd $tmp_dir/amsterdam-schema
mkdir ../changes/${commit}
git archive "$commit" | tar -x -C "../changes/${commit}"

# Return the date on which the update commit was merged (format-local means in timezone of current user)
date=$(git show -s --date=format-local:'%Y-%m-%d %H:%M:%S' --no-patch --format=%cd $commit)
echo "$date"
