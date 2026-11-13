#!/bin/bash
# 公共：连到虚拟机桌面会话（Xorg 或 Wayland/Xwayland 都能用）
# 用法：在其它脚本里 source 这个文件
export DISPLAY=:0
export XDG_RUNTIME_DIR=/run/user/1000
if ls /run/user/1000/.mutter-Xwaylandauth.* >/dev/null 2>&1; then
  # Wayland 会话（Xwayland）
  for f in /run/user/1000/.mutter-Xwaylandauth.*; do
    [ -e "$f" ] && export XAUTHORITY="$f"
  done
  C26_SESSION=wayland
elif [ -f "$HOME/.Xauthority" ]; then
  # Xorg 会话
  export XAUTHORITY="$HOME/.Xauthority"
  C26_SESSION=xorg
elif [ -f /run/user/1000/gdm/Xauthority ]; then
  export XAUTHORITY=/run/user/1000/gdm/Xauthority
  C26_SESSION=xorg
else
  C26_SESSION=unknown
fi
export C26_SESSION
