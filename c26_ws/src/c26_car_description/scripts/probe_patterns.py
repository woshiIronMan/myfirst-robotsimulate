#!/usr/bin/env python3
"""辨识实验：直接给 4 个轮子下发速度模式，测量车身实际运动方向。

目的：不靠猜符号，直接从仿真里测出「轮速模式 -> 车身速度」的映射，
     再用它反解出正确的麦轮解算矩阵。
"""
import math
import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
from nav_msgs.msg import Odometry

W = ["wheel_fl", "wheel_fr", "wheel_rl", "wheel_rr"]
SPEED = 12.0  # rad/s


def yaw_of(q):
    return math.atan2(2.0 * (q.w * q.z + q.x * q.y),
                      1.0 - 2.0 * (q.y * q.y + q.z * q.z))


class Probe(Node):
    def __init__(self):
        super().__init__("c26_probe")
        self.pubs = {w: self.create_publisher(Float64, "/c26/cmd_vel_wheel/" + w, 10)
                     for w in W}
        self.odom = None
        self.create_subscription(Odometry, "/odom", self.cb, 10)

    def cb(self, m):
        self.odom = m

    def spin(self, dur):
        t0 = time.time()
        while time.time() - t0 < dur:
            rclpy.spin_once(self, timeout_sec=0.02)

    def pose(self):
        for _ in range(80):
            self.spin(0.05)
            if self.odom is not None:
                p = self.odom.pose.pose
                return p.position.x, p.position.y, yaw_of(p.orientation)
        raise RuntimeError("no odom")

    def set_wheels(self, vals, dur):
        t0 = time.time()
        while time.time() - t0 < dur:
            for w, v in zip(W, vals):
                self.pubs[w].publish(Float64(data=float(v)))
            self.spin(0.05)

    def stop(self):
        self.set_wheels([0, 0, 0, 0], 0.8)
        self.spin(0.6)


def run_pattern(p, name, vals, dur=1.5):
    p.stop()
    x0, y0, th0 = p.pose()
    p.set_wheels(vals, dur)
    p.stop()
    x1, y1, th1 = p.pose()
    dx, dy = x1 - x0, y1 - y0
    bx = math.cos(th0) * dx + math.sin(th0) * dy
    by = -math.sin(th0) * dx + math.cos(th0) * dy
    dth = math.atan2(math.sin(th1 - th0), math.cos(th1 - th0))
    print("%-28s wheel=%s  ->  body vx=%+.3f m/s  vy=%+.3f m/s  wz=%+.2f rad/s"
          % (name, vals, bx / dur, by / dur, dth / dur))


def main():
    rclpy.init()
    p = Probe()
    p.spin(1.0)
    s = SPEED
    run_pattern(p, "A: all forward", [s, s, s, s])
    run_pattern(p, "B: diag +- -+", [s, -s, -s, s])
    run_pattern(p, "C: left/right +- +-", [s, -s, s, -s])
    run_pattern(p, "D: +- -+ negated", [-s, s, s, -s])
    run_pattern(p, "E: +- +- negated", [-s, s, -s, s])
    run_pattern(p, "F: fl only", [s, 0, 0, 0])
    run_pattern(p, "G: fl+rr", [s, 0, 0, s])
    p.destroy_node()
    rclpy.try_shutdown()


if __name__ == "__main__":
    main()
