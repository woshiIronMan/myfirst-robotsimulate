#!/bin/bash
# 判断是不是「小车进场景」导致视口空白：先只开世界截图，再生成小车截图
export DISPLAY=:0
for f in /run/user/1000/.mutter-Xwaylandauth.*; do
  [ -e "$f" ] && export XAUTHORITY="$f"
done
export XDG_RUNTIME_DIR=/run/user/1000
export QT_X11_NO_MITSHM=1
export QSG_RENDER_LOOP=basic
source /opt/ros/lyrical/setup.bash
source "$HOME/c26_ws/install/setup.bash"

pkill -9 -f '[g]z-sim-main' 2>/dev/null
pkill -9 -f '[g]z-sim-gui-client' 2>/dev/null
sleep 2

WORLD="$HOME/c26_ws/install/c26_car_description/share/c26_car_description/worlds/c26_arena.sdf"
setsid gz sim -r -v 2 "$WORLD" </dev/null >/tmp/t2.log 2>&1 &
sleep 26
mkdir -p /tmp/t2a /tmp/t2b
gz service -s /gui/screenshot --reqtype gz.msgs.StringMsg --reptype gz.msgs.Boolean \
  --timeout 12000 --req 'data: "/tmp/t2a"' >/dev/null 2>&1
sleep 2
echo "before: $(ls -la /tmp/t2a/*.png 2>/dev/null | awk '{print $5}')"

# 生成当前 urdf（planar 模式）
xacro "$HOME/c26_ws/install/c26_car_description/share/c26_car_description/urdf/c26_car.urdf.xacro" \
  planar_drive:=true > /tmp/car.urdf 2>/tmp/xacro2.err
echo "xacro rc=$? lines=$(wc -l < /tmp/car.urdf)"

gz service -s /world/c26_arena/create --reqtype gz.msgs.EntityFactory --reptype gz.msgs.Boolean \
  --timeout 15000 --req 'sdf_filename: "/tmp/car.urdf", name: "c26", allow_renaming: false, pose: {position: {z: 0.05}}' 2>&1 | head -3
sleep 6
gz service -s /gui/screenshot --reqtype gz.msgs.StringMsg --reptype gz.msgs.Boolean \
  --timeout 12000 --req 'data: "/tmp/t2b"' >/dev/null 2>&1
sleep 2
echo "after:  $(ls -la /tmp/t2b/*.png 2>/dev/null | awk '{print $5}')"
echo "--- errors after spawn ---"
grep -inE 'error|ogre|mesh|material|scene' /tmp/t2.log | grep -v GzCard | tail -8
