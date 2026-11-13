#!/bin/bash
# 撤销 AccountsService 里的 XSession 设置（26.04 没有 Xorg 会话，留着会登录失败）
set -e
ACCT=/var/lib/AccountsService/users/xue
sed -i '/^XSession=/d' "$ACCT"
# 同时把 gdm 的 WaylandEnable=false 也改回去，避免与自动登录冲突
sed -i 's/^WaylandEnable=.*/WaylandEnable=true/' /etc/gdm3/custom.conf
echo "--- AccountsService ---"
cat "$ACCT"
echo "--- gdm ---"
grep -n 'WaylandEnable' /etc/gdm3/custom.conf
