#!/bin/bash
# 强制 xue 用户使用 Xorg 会话（AccountsService + gdm 配置），然后重启桌面会话
set -e
ACCT=/var/lib/AccountsService/users/xue
echo "--- before ---"
cat "$ACCT"

if grep -q '^XSession=' "$ACCT"; then
  sed -i 's/^XSession=.*/XSession=ubuntu-xorg/' "$ACCT"
else
  if grep -q '^\[User\]' "$ACCT"; then
    sed -i '/^\[User\]/a XSession=ubuntu-xorg' "$ACCT"
  else
    printf '[User]\nXSession=ubuntu-xorg\n' >> "$ACCT"
  fi
fi

echo "--- after ---"
cat "$ACCT"
echo "--- xorg session available? ---"
ls /usr/share/xsessions/ 2>/dev/null
