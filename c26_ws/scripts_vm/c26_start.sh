#!/bin/bash
# C26 仿真启动脚本
# 用法: c26_start.sh [gui|headless] [world.sdf]
set -e
MODE="${1:-headless}"
WORLD="${2:-default}"

source /opt/ros/lyrical/setup.bash
source "$HOME/c26_ws/install/setup.bash"
source "$HOME/c26_xenv.sh"

WORLD_PATH="$WORLD"
if [ "$WORLD" = "default" ] || [ -z "$WORLD" ]; then
  WORLD_PATH="$HOME/c26_ws/install/c26_car_description/share/c26_car_description/worlds/c26_arena.sdf"
fi

if [ -f /tmp/c26_launch.pid ] && kill -0 "$(cat /tmp/c26_launch.pid)" 2>/dev/null; then
  echo "already running, pid $(cat /tmp/c26_launch.pid)"
  exit 0
fi

# 若已有残留仿真在跑，先清掉，避免多个 world 抢 /clock 导致数据错乱
if pgrep -f "gz-sim-main" >/dev/null 2>&1; then
  echo "cleaning leftover gz-sim processes..."
  bash "$HOME/c26_stop.sh" >/dev/null 2>&1 || true
  sleep 2
fi

setsid ros2 launch c26_car_description c26_gazebo.launch.py \
  headless:=true world:="$WORLD_PATH" \
  </dev/null >/tmp/c26_launch.log 2>&1 &
echo $! > /tmp/c26_launch.pid
echo "server started pid $(cat /tmp/c26_launch.pid) log=/tmp/c26_launch.log (session=$C26_SESSION)"

if [ "$MODE" = "gui" ]; then
  sleep 6
  # 用包里自带的 gui.config：初始机位就在车旁边（默认机位在 8.5m 外，车只有 27 像素）
  GUI_CFG="$HOME/c26_ws/install/c26_car_description/share/c26_car_description/config/gui.config"
  # 独立的 GUI 客户端也需要解析 package:// 网格资源。
  export GZ_SIM_RESOURCE_PATH="$(dirname "$(ros2 pkg prefix --share c26_car_description)")${GZ_SIM_RESOURCE_PATH:+:$GZ_SIM_RESOURCE_PATH}"
  # VMware SVGA3D 会让 Ogre2 视口间歇空白。Qt 通过 GLX 使用 Mesa 软件渲染。
  setsid env QT_QPA_PLATFORM=xcb QT_XCB_GL_INTEGRATION=xcb_glx \
    QT_X11_NO_MITSHM=1 QSG_RENDER_LOOP=basic LIBGL_ALWAYS_SOFTWARE=1 \
    gz sim -g -v 2 --gui-config "$GUI_CFG" "$WORLD_PATH" \
    </dev/null >/tmp/c26_gui.log 2>&1 &
  echo $! > /tmp/c26_gui.pid
  echo "gui started pid $(cat /tmp/c26_gui.pid) log=/tmp/c26_gui.log"
fi
