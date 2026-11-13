#!/bin/bash
# 在虚拟机终端运行，按键通过 /cmd_vel 控制 C26。
set -e
source /opt/ros/lyrical/setup.bash
source "$HOME/c26_ws/install/setup.bash"

echo '请让此终端保持焦点。按住 i 前进、逗号后退、j/l 原地左/右转。'
echo 'Shift+j / Shift+l 左/右横移，空格或 k 停车，Ctrl+C 退出。'
exec ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args -p speed:=0.2 -p turn:=0.5
