#!/bin/bash
# 用官方 shapes.sdf 测试 GUI 渲染是否正常（判断是环境问题还是我们场景的问题）
export DISPLAY=:0
for f in /run/user/1000/.mutter-Xwaylandauth.*; do
  [ -e "$f" ] && export XAUTHORITY="$f"
done
export XDG_RUNTIME_DIR=/run/user/1000
export LIBGL_ALWAYS_SOFTWARE=1
export GALLIUM_DRIVER=llvmpipe
export QT_X11_NO_MITSHM=1
export QSG_RENDER_LOOP=basic
source /opt/ros/lyrical/setup.bash

WORLD=$(ls /opt/ros/lyrical/opt/gz_sim_vendor/share/gz/gz-sim10/worlds/shapes.sdf 2>/dev/null)
echo "world=$WORLD"
setsid gz sim -r "$WORLD" </dev/null >/tmp/shapes.log 2>&1 &
echo $! > /tmp/shapes.pid
sleep 25
mkdir -p /tmp/shapeshots
gz service -s /gui/screenshot --reqtype gz.msgs.StringMsg --reptype gz.msgs.Boolean \
  --timeout 10000 --req 'data: "/tmp/shapeshots"' 2>&1 | head -3
sleep 2
ls -la /tmp/shapeshots/ | tail -3
echo "--- gui errors ---"
grep -iE 'error|warn.*render|ogre' /tmp/shapes.log | head -8
