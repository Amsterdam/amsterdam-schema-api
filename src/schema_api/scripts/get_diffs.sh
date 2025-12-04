#!/bin/bash


# Clone Amsterdam Schema repo
#mkdir tmp
#cd tmp
#mkdir diffs
#git clone git@github.com:Amsterdam/amsterdam-schema.git
#echo "Cloned!"

# Do actual command (temporarily only get the latest 5 commits)
cd tmp/amsterdam-schema
#git pull
#git fetch origin master
commits=$(git log --first-parent master -10 --pretty=format:"%h")

# Store commits in an actual array
original_array=()
for commit in $commits; do
    original_array+=("$commit")
done
echo "${original_array[@]}"

# Reverse the array
reversed_commits=()
for ((i=${#original_array[@]}-1; i>=0; i--)); do
    reversed_commits+=("${original_array[i]}")
done
echo "${reversed_commits[@]}"
echo
echo "${reversed_commits[2]}"
echo "${reversed_commits[3]}"
echo

base_commit=""
for new_commit in ${reversed_commits[@]}
do
    echo "$new_commit"
    if [ -z "$base_commit" ]; then
        echo "Empty base commit, skipping..."

    elif [ $new_commit = "04b896ea" ]; then

        date=$(git show -s --date=format:'%Y-%m-%d' --no-patch --format=%cd $new_commit)
        echo "Non empty base commit:"
        echo "Base commit:"
        echo "$base_commit"
        echo "Update commit:"
        echo "$new_commit"
        echo "$date"

        new_commit="b2d6f8f"
        base_commit="52a479a"


        mkdir ../changes/${new_commit}
        mkdir ../changes/${base_commit}

        git archive "$new_commit" | tar -x -C "../changes/${new_commit}"
        git archive "$base_commit" | tar -x -C "../changes/${base_commit}"

    fi
    base_commit=$new_commit
done


# Clean up will not be done in this file
# Clean up diff folder
#cd ..
#rm -rf diff

# Clean up tmp folder
# cd ../
# rm -rf tmp
