#!/bin/bash
# 只重启 GUI 客户端（服务器保持运行）
source "$HOME/c26_xenv.sh"
source /opt/ros/lyrical/setup.bash
source "$HOME/c26_ws/install/setup.bash"
WORLD="$HOME/c26_ws/install/c26_car_description/share/c26_car_description/worlds/c26_arena.sdf"

pkill -9 -f 'gz-sim-gui-client' 2>/dev/null
sleep 3
echo "server alive: $(pgrep -f 'gz-sim-main -s' | wc -l)"
setsid gz sim -g -v 2 "$WORLD" </dev/null >/tmp/c26_gui.log 2>&1 &
echo "gui launched pid $!"
sleep 20
echo "gui alive: $(pgrep -f 'gz-sim-gui-client' | wc -l)"
