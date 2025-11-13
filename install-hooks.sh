#!/bin/bash

# Git Hooks 安装脚本
# 此脚本用于自动配置 Git 使用项目中的 hooks 目录

echo "开始安装 Git Hooks..."

# 1. 配置 Git 使用自定义钩子路径
echo "正在配置 Git 钩子路径..."
git config core.hooksPath hooks

# 2. 赋予钩子脚本执行权限
echo "正在赋予钩子脚本执行权限..."
cd hooks
find . -type f -exec chmod +x {} \;
cd ..

# 3. 验证配置
echo ""
echo "验证配置..."
HOOKS_PATH=$(git config core.hooksPath)
if [ "$HOOKS_PATH" = "hooks" ]; then
    echo "✓ Git 钩子路径配置成功: $HOOKS_PATH"
else
    echo "✗ Git 钩子路径配置失败"
    exit 1
fi

# 4. 列出已安装的钩子
echo ""
echo "已安装的钩子:"
ls -lh hooks/

echo ""
echo "Git Hooks 安装完成！"
