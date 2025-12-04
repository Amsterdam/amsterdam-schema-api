# Clone Amsterdam Schema repo

#mkdir tmp
#cd tmp
#mkdir changes
#echo "Cloning Amsterdam Schema repo..."
#git clone git@github.com:Amsterdam/amsterdam-schema.git
#echo "Done!"


# Fetch history of commits into master (oldest to newest)
cd tmp/amsterdam-schema
git pull
git fetch origin master

# TODO: define start commit to start changelog from
# as argument for management command
# Handy for where to start from when updating the changelog database
commits=$(git log --first-parent master -15 --pretty=format:"%h")

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

# Save the array
printf "%s\n" "${reversed_commits[@]}" > ../commits.txt
