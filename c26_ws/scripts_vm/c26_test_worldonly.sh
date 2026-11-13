#!/bin/bash
# 隔离测试：只加载世界（不含小车），看能否渲染出彩色参照方块
export DISPLAY=:0
for f in /run/user/1000/.mutter-Xwaylandauth.*; do
  [ -e "$f" ] && export XAUTHORITY="$f"
done
export XDG_RUNTIME_DIR=/run/user/1000
export QT_X11_NO_MITSHM=1
export QSG_RENDER_LOOP=basic
source /opt/ros/lyrical/setup.bash

pkill -9 -f '[g]z-sim-main' 2>/dev/null
pkill -9 -f '[g]z-sim-gui-client' 2>/dev/null
sleep 2

WORLD="$HOME/c26_ws/install/c26_car_description/share/c26_car_description/worlds/c26_arena.sdf"
setsid gz sim -r -v 2 "$WORLD" </dev/null >/tmp/world_only.log 2>&1 &
sleep 28
mkdir -p /tmp/w1
gz service -s /gui/screenshot --reqtype gz.msgs.StringMsg --reptype gz.msgs.Boolean \
  --timeout 12000 --req 'data: "/tmp/w1"' 2>&1 | head -2
sleep 2
ls -lat /tmp/w1/*.png 2>/dev/null | head -2
