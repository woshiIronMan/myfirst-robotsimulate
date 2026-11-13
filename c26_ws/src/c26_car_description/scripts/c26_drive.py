#!/usr/bin/env python3
"""给小车一个速度指令，持续若干秒后自动停。

用法:
    python3 c26_drive.py VX VY WZ [SECONDS]
例:
    python3 c26_drive.py 0.20 0 0 2      # 前进 0.2 m/s，2 秒
    python3 c26_drive.py 0 0.20 0 2      # 向左横移
    python3 c26_drive.py 0 0 0.5 2       # 原地左转
    python3 c26_drive.py 0.15 0.10 0 3   # 斜着走
"""
import sys
import time

import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from geometry_msgs.msg import Twist


def main():
    args = sys.argv[1:]
    if len(args) < 3:
        print(__doc__)
        return 1
    vx, vy, wz = (float(a) for a in args[:3])
    dur = float(args[3]) if len(args) > 3 else 2.0

    rclpy.init()
    node = Node("c26_drive")
    node.set_parameters([Parameter("use_sim_time", Parameter.Type.BOOL, True)])
    # 等仿真时钟
    t0 = time.time()
    pub = node.create_publisher(Twist, "/cmd_vel", 10)
    while time.time() - t0 < 5 and node.get_clock().now().nanoseconds <= 0:
        rclpy.spin_once(node, timeout_sec=0.05)

    cmd = Twist()
    cmd.linear.x = vx
    cmd.linear.y = vy
    cmd.angular.z = wz
    print("cmd vx=%.2f vy=%.2f wz=%.2f for %.1fs(仿真时间)" % (vx, vy, wz, dur))

    def sim_now():
        return node.get_clock().now().nanoseconds * 1e-9

    # 按仿真时间计时（Gazebo GUI 下实时因子 <1，按墙钟会跑不够）
    t0 = sim_now()
    while sim_now() - t0 < dur:
        pub.publish(cmd)
        rclpy.spin_once(node, timeout_sec=0.02)
    stop = Twist()
    for _ in range(20):
        pub.publish(stop)
        rclpy.spin_once(node, timeout_sec=0.02)
    node.destroy_node()
    rclpy.try_shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
