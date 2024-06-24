#!/bin/zsh
if [ -z "$1" ]
  then
    echo "No commit message supplied"
    exit 1
fi

COMMIT_MESSAGE=$1

git pull

git add .
git commit -m "$COMMIT_MESSAGE"
git push origin master

echo "Changes have been committed and pushed to GitHub."
