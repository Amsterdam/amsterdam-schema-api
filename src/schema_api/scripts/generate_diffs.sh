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

        change_dir="${new_commit}_${date}"
        echo "$change_dir"
        mkdir ../changes/${change_dir}
        #git --no-pager diff --name-only --diff-filter=M $commit $prev_commit -- 'datasets/**/v[0-9]*.json' > ../diffs/${prev_commit}_${commit}_diff.txt
        modified_tables=$(git --no-pager diff --name-only --diff-filter=M $base_commit $new_commit -- 'datasets/**/v[0-9]*.json')

        if [ -n "$modified_tables" ]; then

            # For all tables label modify.
            label="m"

            # Loop through all modified table files
            for table_path in $modified_tables
            do
                echo "$table_path"
                table_name="${table_path//\//_}"
                echo "$table_name"

                # Save base and updated table
                git checkout $new_commit $table_path
                cat "$table_path" > ../changes/${change_dir}/m_${new_commit}_${table_name}

                git checkout $base_commit $table_path
                cat "$table_path" > ../changes/${change_dir}/m_${base_commit}_${table_name}

                # Extract dataset
                IFS='/' read -a array <<< "$table_path"
                dataset=${array[1]}
                dataset_path="${array[0]}/${array[1]}/dataset.json"
                dataset_name="${dataset_path//\//_}"
                echo "$dataset"
                echo "$dataset_path"
                echo "$dataset_name"

                # Save modified dataset
                git checkout $new_commit $dataset_path
                cat "$dataset_path" > ../changes/${change_dir}/m_${new_commit}_${dataset_name}

                git checkout $base_commit $dataset_path
                cat "$dataset_path" > ../changes/${change_dir}/m_${base_commit}_${dataset_name}
            done
        fi
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
