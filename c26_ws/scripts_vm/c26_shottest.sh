#!/bin/bash
export DISPLAY=:0
for f in /run/user/1000/.mutter-Xwaylandauth.*; do
  [ -e "$f" ] && export XAUTHORITY="$f"
done
export XDG_RUNTIME_DIR=/run/user/1000
echo "which xwd: $(which xwd 2>/dev/null || echo none)"
echo "which import: $(which import 2>/dev/null || echo none)"
echo "which gnome-screenshot: $(which gnome-screenshot 2>/dev/null || echo none)"
echo "--- try import plain ---"
rm -f /tmp/shot_plain.png
timeout 40 import -window root /tmp/shot_plain.png 2>&1 | head -3
ls -la /tmp/shot_plain.png 2>/dev/null || echo "PLAIN_FAILED"
echo "--- try flameshot/scrot? ---"
which scrot flameshot 2>/dev/null || true
