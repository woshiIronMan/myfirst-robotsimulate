#!/bin/bash
# 渲染稳定性测试：连拍 3 张，看是否都有内容（文件大小应接近且不为空图）
cd "$HOME" || exit 1
bash "$HOME/c26_stop.sh" >/dev/null 2>&1 || true
sleep 2
bash "$HOME/c26_start.sh" gui
sleep 34
source /opt/ros/lyrical/setup.bash
source "$HOME/c26_ws/install/setup.bash"
for i in 1 2 3; do
  D="/tmp/stab$i"
  mkdir -p "$D"
  gz service -s /gui/screenshot --reqtype gz.msgs.StringMsg --reptype gz.msgs.Boolean \
    --timeout 12000 --req "data: \"$D\"" >/dev/null 2>&1
  sleep 3
  echo "shot$i: $(ls -la $D/*.png 2>/dev/null | awk '{print $5}' | tail -1)"
done
echo "--- glxinfo in gui env ---"
export LIBGL_DEBUG=quiet
echo "--- errors ---"
grep -inE 'error|ogre|egl' /tmp/c26_gui.log 2>/dev/null | head -5
