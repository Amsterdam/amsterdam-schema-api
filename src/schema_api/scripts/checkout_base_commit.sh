#!/bin/bash
set -e

# Load base commit and tmp_dir
base_commit=$1
tmp_dir=$2

# Checkout base commit
cd $tmp_dir/amsterdam-schema
mkdir ../changes/${base_commit}
git archive "$base_commit" | tar -x -C "../changes/${base_commit}"
