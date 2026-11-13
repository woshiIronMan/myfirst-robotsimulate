#!/bin/bash
# 测试：单进程 GUI（server+gui 同一个进程），配合已精简的物理
export DISPLAY=:0
for f in /run/user/1000/.mutter-Xwaylandauth.*; do
  [ -e "$f" ] && export XAUTHORITY="$f"
done
export XDG_RUNTIME_DIR=/run/user/1000
export QT_X11_NO_MITSHM=1
export QSG_RENDER_LOOP=basic
source /opt/ros/lyrical/setup.bash
source "$HOME/c26_ws/install/setup.bash"

bash "$HOME/c26_stop.sh" >/dev/null 2>&1 || true
sleep 2

WORLD="$HOME/c26_ws/install/c26_car_description/share/c26_car_description/worlds/c26_arena.sdf"
setsid ros2 launch c26_car_description c26_gazebo.launch.py \
  headless:=false world:="$WORLD" </dev/null >/tmp/c26_single.log 2>&1 &
echo $! > /tmp/c26_launch.pid
echo "single-process launch pid $!"

sleep 32
mkdir -p /tmp/sp3
gz service -s /gui/screenshot --reqtype gz.msgs.StringMsg --reptype gz.msgs.Boolean \
  --timeout 10000 --req 'data: "/tmp/sp3"' 2>&1 | head -2
sleep 2
ls -lat /tmp/sp3/*.png 2>/dev/null | head -2
echo "--- stats ---"
timeout 15 gz topic -e -t /stats -n 1 2>/dev/null | grep -E 'real_time_factor|sim_time|iteration' | head -4
