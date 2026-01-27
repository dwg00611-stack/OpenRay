#!/bin/bash
set -e

# Activate virtual environment
source /mnt/c/d/Development/OpenRay/.venv/bin/activate

# Go to repo
cd /mnt/c/d/Development/OpenRay

# Try git pull, fallback to merge if it fails
if ! git pull origin main; then
    echo "git pull failed, retrying with merge..."
    git pull --no-edit origin main --no-rebase
fi

# Clean git conflict markers and duplicates from data files immediately after git operations
echo "Cleaning data files from git conflicts and duplicates..."
python3 clean_data.py

# Run your Python script
python3 -m src.main_for_iran

# Convert subscription to Clash and Singbox formats
echo "Converting Iran subscription to config formats..."
python src/converter/sub2clash_singbox.py ./output_iran/iran_top100_checked.txt src/converter/config.yaml src/converter/singbox.json ./output_iran/converted/iran_top100_clash_config.yaml ./output_iran/converted/iran_top100_singbox_config.json

# Check if there are changes before committing
if [ -n "$(git status --porcelain)" ]; then
    git add .
    git commit -m "Auto update for iran: $(date '+%Y-%m-%d %H:%M:%S')"

     # Push (local always wins)
    if ! git push origin main; then
        echo "Push failed, forcing local state to remote..."

        # Clean conflict markers again after merge/pull
        echo "Cleaning data files from conflicts after merge..."
        python3 clean_data.py

        git fetch origin
        git push origin main --force-with-lease
    fi
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] No changes to commit."
fi
