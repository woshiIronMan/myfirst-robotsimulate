#!/bin/bash
# 把 GNOME 会话从 Wayland 切到 Xorg（修复 Gazebo GUI 闪烁/空白）
set -e
cp -n /etc/gdm3/custom.conf /etc/gdm3/custom.conf.bak || true
if grep -q '^WaylandEnable' /etc/gdm3/custom.conf; then
  sed -i 's/^WaylandEnable=.*/WaylandEnable=false/' /etc/gdm3/custom.conf
else
  sed -i '/^\[daemon\]/a WaylandEnable=false' /etc/gdm3/custom.conf
fi
echo "--- after ---"
head -10 /etc/gdm3/custom.conf
