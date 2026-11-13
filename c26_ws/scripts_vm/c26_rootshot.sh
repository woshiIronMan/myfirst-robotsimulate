#!/bin/bash
# 抓 Xwayland 根窗口（整屏）截图：xwd + ImageMagick 转换
export DISPLAY=:0
for f in /run/user/1000/.mutter-Xwaylandauth.*; do
  [ -e "$f" ] && export XAUTHORITY="$f"
done
export XDG_RUNTIME_DIR=/run/user/1000
OUT="${1:-/tmp/root_shot.png}"
rm -f /tmp/root_shot.xwd "$OUT"
timeout 40 xwd -root -silent > /tmp/root_shot.xwd 2>/tmp/xwd.err
echo "xwd rc=$? size=$(stat -c%s /tmp/root_shot.xwd 2>/dev/null)"
head -2 /tmp/xwd.err 2>/dev/null
if [ -s /tmp/root_shot.xwd ]; then
  timeout 60 convert /tmp/root_shot.xwd "$OUT" 2>&1 | head -3
  ls -la "$OUT" 2>/dev/null || echo "CONVERT_FAILED"
else
  echo "XWD_FAILED"
fi
