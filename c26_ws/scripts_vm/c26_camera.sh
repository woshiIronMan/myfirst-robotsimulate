#!/bin/bash
# 把 Gazebo GUI 的相机移到小车附近（默认机位在 8.5m 外，车只有几十像素）
source /opt/ros/lyrical/setup.bash
source "$HOME/c26_ws/install/setup.bash"
source "$HOME/c26_xenv.sh"

# 相机位置 (0.85,-0.85,0.55) 朝向原点，四元数预先算好
gz service -s /gui/move_to/pose \
  --reqtype gz.msgs.Pose --reptype gz.msgs.Boolean --timeout 8000 \
  --req 'name: "car_view", position: {x: 0.85, y: -0.85, z: 0.55}, orientation: {x: 0.1812, y: -0.0750, z: 0.9060, w: 0.3753}' \
  2>&1 | head -5
