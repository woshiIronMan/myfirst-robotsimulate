#!/bin/bash
# 检查截图文件位置 + GUI 客户端进程的环境变量
echo "--- recent png ---"
find /home/xue /tmp -name 'gui_view*.png' -newermt '-15 minutes' 2>/dev/null | head -5
ls -la /tmp/*.png 2>/dev/null | tail -6
echo "--- gui client env ---"
P=$(pgrep -f 'gz-sim-gui-client' | tail -1)
echo "gui pid=$P"
if [ -n "$P" ]; then
  tr '\0' '\n' < "/proc/$P/environ" | grep -E '^(LIBGL|GALLIUM|DISPLAY|XAUTHORITY|QSG|QT_X11)' || echo "(no GL env vars)"
fi
