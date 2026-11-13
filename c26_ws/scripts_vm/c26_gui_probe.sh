#!/bin/bash
# 用 Gazebo GUI 截图服务抓视口图（data 是**目录**，插件自己拼时间戳文件名）
source /opt/ros/lyrical/setup.bash
source "$HOME/c26_ws/install/setup.bash"
source "$HOME/c26_xenv.sh"

OUTDIR="${1:-/tmp/gzshots}"
mkdir -p "$OUTDIR"
BEFORE=$(ls -1 "$OUTDIR"/*.png 2>/dev/null | wc -l)
gz service -s /gui/screenshot --reqtype gz.msgs.StringMsg --reptype gz.msgs.Boolean \
  --timeout 12000 --req "data: \"$OUTDIR\"" 2>&1 | head -3
sleep 2
AFTER=$(ls -1 "$OUTDIR"/*.png 2>/dev/null | wc -l)
echo "png count: $BEFORE -> $AFTER"
ls -lat "$OUTDIR"/*.png 2>/dev/null | head -2
