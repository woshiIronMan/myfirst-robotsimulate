#!/bin/bash
# 单进程模式（server+gui 同进程）+ 俯视机位，连拍两张看是否有内容
source "$HOME/c26_xenv.sh"
source /opt/ros/lyrical/setup.bash
source "$HOME/c26_ws/install/setup.bash"
WORLD="$HOME/c26_ws/install/c26_car_description/share/c26_car_description/worlds/c26_arena.sdf"

bash "$HOME/c26_stop.sh" >/dev/null 2>&1 || true
sleep 2
setsid gz sim -r -v 2 "$WORLD" </dev/null >/tmp/c26_single.log 2>&1 &
sleep 28
for i in 1 2; do
  D="/tmp/s$i"; mkdir -p "$D"
  gz service -s /gui/screenshot --reqtype gz.msgs.StringMsg --reptype gz.msgs.Boolean \
    --timeout 12000 --req "data: \"$D\"" >/dev/null 2>&1
  sleep 3
  echo "shot$i size: $(ls -la $D/*.png 2>/dev/null | awk '{print $5}' | tail -1)"
done
echo "--- ogre errors ---"
grep -icE 'ogre.*(error|exception)' /tmp/c26_single.log
