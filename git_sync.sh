#!/bin/zsh

# 获取提交消息
if [ -z "$1" ]
  then
    echo "No commit message supplied"
    exit 1
fi

COMMIT_MESSAGE=$1

git pull
# 添加所有更改到暂存区
git add .

# 提交更改
git commit -m "$COMMIT_MESSAGE"

# 推送到远程仓库
git push origin master

echo "Changes have been committed and pushed to GitHub."
