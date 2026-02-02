#!/bin/bash
set -e

# Parse command line arguments
SKIP_GIT=false
PYTHON_FLAGS=""

for arg in "$@"; do
    if [ "$arg" == "--skip-git" ]; then
        SKIP_GIT=true
        echo "Running with --skip-git flag: Git operations will be skipped"
    else
        # Collect all other arguments to pass to Python script
        PYTHON_FLAGS="$PYTHON_FLAGS $arg"
    fi
done

# Activate virtual environment
source /mnt/c/d/Development/OpenRay/.venv/bin/activate

# Go to repo
cd /mnt/c/d/Development/OpenRay

# Git pull operations (only if not skipping)
if [ "$SKIP_GIT" = false ]; then
    # Try git pull, fallback to merge if it fails
    if ! git pull origin main; then
        echo "git pull failed, retrying with merge..."
        git pull --no-edit origin main --no-rebase
    fi

    # Clean git conflict markers and duplicates from data files immediately after git operations
    echo "Cleaning data files from git conflicts and duplicates..."
    python3 clean_data.py
else
    echo "Skipping git pull operations..."
fi

# Run your Python script with collected flags
echo "Running Python script with flags:$PYTHON_FLAGS"
python3 -m src.main_for_iran$PYTHON_FLAGS

# Convert subscription to Clash and Singbox formats
echo "Converting Iran subscription to config formats..."
python src/converter/sub2clash_singbox.py ./output_iran/iran_top100_checked.txt src/converter/config.yaml src/converter/singbox.json ./output_iran/converted/iran_top100_clash_config.yaml ./output_iran/converted/iran_top100_singbox_config.json

# Git commit and push operations (only if not skipping)
if [ "$SKIP_GIT" = false ]; then
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
else
    echo "Skipping git commit and push operations..."
fi