# Clone Amsterdam Schema repo

start_commit=$1
end_commit="HEAD"
echo "Generating changelog from commit:"
echo $start_commit
echo ""

mkdir tmp
cd tmp
mkdir changes
echo "Cloning Amsterdam Schema repo..."
git clone git@github.com:Amsterdam/amsterdam-schema.git
echo "Done!"


# Fetch history of commits into master (oldest to newest)
cd amsterdam-schema
#git pull
#git fetch origin master

commits=$(git log $start_commit^..$end_commit --first-parent master --pretty=format:"%H")

# Store commits in an actual array
original_array=()
for commit in $commits; do
    original_array+=("$commit")
done

# Reverse the array
reversed_commits=()
for ((i=${#original_array[@]}-1; i>=0; i--)); do
    reversed_commits+=("${original_array[i]}")
done

# Save the array
printf "%s\n" "${reversed_commits[@]}" > ../commits.txt
