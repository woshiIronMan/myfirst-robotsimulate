#!/bin/bash
# 在虚拟机的桌面会话 (Wayland/Xwayland :0) 上启动 Gazebo GUI，并截图
export DISPLAY=:0
for f in /run/user/1000/.mutter-Xwaylandauth.*; do
  [ -e "$f" ] && export XAUTHORITY="$f"
done
export XDG_RUNTIME_DIR=/run/user/1000
echo "DISPLAY=$DISPLAY XAUTHORITY=$XAUTHORITY"

# 1) 测试能否连上 X
if command -v xdpyinfo >/dev/null; then
  xdpyinfo >/dev/null 2>&1 && echo "X_OK" || echo "X_FAIL"
else
  python3 -c "import ctypes,sys; sys.exit(0)" && echo "no-xdpyinfo"
fi

# 2) 截图测试
gnome-screenshot -f /tmp/test_shot.png 2>&1 && echo "SHOT_OK" || echo "SHOT_FAIL"
ls -la /tmp/test_shot.png 2>/dev/null
