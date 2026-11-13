#!/bin/bash
export DISPLAY=:0
for f in /run/user/1000/.mutter-Xwaylandauth.*; do
  [ -e "$f" ] && export XAUTHORITY="$f"
done
export XDG_RUNTIME_DIR=/run/user/1000
echo "--- X windows ---"
timeout 20 xwininfo -root -tree 2>&1 | head -25
echo "--- GUI client CPU ---"
ps -eo pid,pcpu,pmem,etimes,args | grep '[g]z-sim' | cut -c1-100
echo "--- session type ---"
loginctl show-session $(loginctl | awk '/seat0/ {print $1}' | head -1) -p Type 2>/dev/null
