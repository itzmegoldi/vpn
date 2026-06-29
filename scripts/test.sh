#!/bin/sh

echo "All arguments: $@"

local_branch=$(git rev-parse --abbrev-ref HEAD)
remote_branch=$(git rev-parse --abbrev-ref @{upstream} 2>/dev/null)

if [ -z "$remote_branch" ]; then
    echo "No remote branch configured."
else
    echo "Pushing changes from $local_branch to $remote_branch"
    echo "Checking for changes..."

    if git diff --quiet "$local_branch" "$remote_branch"; then
        echo "No changes detected."
        exit 0
    fi
fi

echo "Running pytest with coverage..."

. .venv/bin/activate

APP_ENV=test pytest --cov=src --tb=no --cov-fail-under=80
status=$?

deactivate

if [ $status -eq 0 ]; then
    echo "✅ Tests passed."
    echo "✅ Coverage check passed."
    exit 0
else
    echo "❌ Tests failed."
    echo "❌ Coverage check failed."
    exit 1
fi