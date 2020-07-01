#! /usr/bin/env bash

IGNORE_DIFF_ON="README.md CONTRIBUTING.md Makefile .gitignore .circleci/* .github/*"

remote_tags_exist=`git ls-remote --tags origin`

if [[ $remote_tags_exist ]];
then
  # get last tagged commit
  commit_to_compare_to=`git describe --tags --abbrev=0 --first-parent`  # --first-parent ensures we don't follow tags not published in master through an unlikely intermediary merge commit
else
  # get remote master branch last commit
  commit_to_compare_to=`git rev-parse origin/master`
fi


if git diff-index --name-only --exit-code $commit_to_compare_to -- . `echo " $IGNORE_DIFF_ON" | sed 's/ / :(exclude)/g'`  # Check if any file that has not be listed in IGNORE_DIFF_ON has changed since the last tag was published.
then
  echo "No functional changes detected."
  exit 1
else
  echo "The functional files above were changed."
fi
