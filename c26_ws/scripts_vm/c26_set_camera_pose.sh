#!/bin/bash
# 把 GUI 初始机位改到车跟前（gui.config 里的 camera_pose）
CFG="$HOME/.gz/sim/10/gui.config"
if [ ! -f "$CFG" ]; then
  echo "no gui.config: $CFG"
  exit 1
fi
cp -n "$CFG" "$CFG.bak" 2>/dev/null || true
# 原来: <camera_pose>-6 0 6 0 0.5 0</camera_pose>
sed -i 's|<camera_pose>.*</camera_pose>|<camera_pose>0.85 -0.85 0.55 0 -0.3948 2.3562</camera_pose>|' "$CFG"
grep -n 'camera_pose' "$CFG"
