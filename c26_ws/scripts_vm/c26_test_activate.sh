#!/bin/bash
# 测试：把 Gazebo 窗口激活（置前）后视口是否恢复渲染
export DISPLAY=:0
for f in /run/user/1000/.mutter-Xwaylandauth.*; do
  [ -e "$f" ] && export XAUTHORITY="$f"
done
export XDG_RUNTIME_DIR=/run/user/1000
export QT_X11_NO_MITSHM=1
export QSG_RENDER_LOOP=basic
source /opt/ros/lyrical/setup.bash

echo "--- windows ---"
wmctrl -l 2>&1 | head -8
echo "--- activate ---"
wmctrl -a "Gazebo Sim" 2>&1 | head -3
sleep 3
mkdir -p /tmp/act
gz service -s /gui/screenshot --reqtype gz.msgs.StringMsg --reptype gz.msgs.Boolean \
  --timeout 12000 --req 'data: "/tmp/act"' >/dev/null 2>&1
sleep 2
ls -la /tmp/act/*.png 2>/dev/null | tail -2
