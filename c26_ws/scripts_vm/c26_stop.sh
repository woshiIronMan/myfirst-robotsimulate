#!/bin/bash
# 停止 C26 仿真（launch + gz server + gui + bridge + 节点）
# 注意：真正的服务进程名是 gz-sim-main / gz-sim-gui-client，不是 "gz sim"
pkill -9 -f "ros2 launch c26_car_description" 2>/dev/null
pkill -9 -f "gz-sim-main" 2>/dev/null
pkill -9 -f "gz-sim-gui-client" 2>/dev/null
pkill -9 -f "gz_tools_vendor/bin/gz" 2>/dev/null
pkill -9 -f "ros_gz_bridge/parameter_bridge" 2>/dev/null
pkill -9 -f "c26_car_description/mecanum_drive.py" 2>/dev/null
pkill -9 -f "robot_state_publisher" 2>/dev/null
sleep 2
LEFT=$(pgrep -f "gz-sim-main" | wc -l)
rm -f /tmp/c26_launch.pid
if [ "$LEFT" != "0" ]; then
  echo "WARN: still $LEFT gz-sim-main left"
  pgrep -af "gz-sim-main"
else
  echo "stopped"
fi
