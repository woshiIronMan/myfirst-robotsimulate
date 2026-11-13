#!/bin/bash
# 抓取虚拟机桌面截图 -> /tmp/shot.png
export DISPLAY=:0
for f in /run/user/1000/.mutter-Xwaylandauth.*; do
  [ -e "$f" ] && export XAUTHORITY="$f"
done
export XDG_RUNTIME_DIR=/run/user/1000
OUT="${1:-/tmp/shot.png}"
if command -v import >/dev/null 2>&1; then
  timeout 25 import -window root "$OUT" 2>&1 && echo "SHOT_OK import"
elif command -v xwd >/dev/null 2>&1; then
  timeout 25 xwd -root -silent > /tmp/shot.xwd 2>&1 && echo "SHOT_XWD"
else
  timeout 25 gnome-screenshot -f "$OUT" 2>&1 && echo "SHOT_OK gnome"
fi
ls -la "$OUT" 2>/dev/null
