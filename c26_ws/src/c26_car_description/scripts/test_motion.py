#!/usr/bin/env python3
"""运动学自检（按仿真时间计时）：前进 / 横移 / 旋转，报告机体速度与偏航角速度。"""
import math
import time

import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry


def yaw_of(q):
    return math.atan2(2.0 * (q.w * q.z + q.x * q.y),
                      1.0 - 2.0 * (q.y * q.y + q.z * q.z))


class Tester(Node):
    def __init__(self):
        super().__init__("c26_motion_test")
        self.set_parameters([Parameter("use_sim_time", Parameter.Type.BOOL, True)])
        self.pub = self.create_publisher(Twist, "/cmd_vel", 10)
        self.last = None
        self.create_subscription(Odometry, "/odom", self.cb, 10)

    def cb(self, msg):
        self.last = msg

    def sim_now(self):
        return self.get_clock().now().nanoseconds * 1e-9

    def spin_wall(self, dur):
        t0 = time.time()
        while time.time() - t0 < dur:
            rclpy.spin_once(self, timeout_sec=0.02)

    def sim_sleep(self, dur):
        t0 = self.sim_now()
        while self.sim_now() - t0 < dur:
            rclpy.spin_once(self, timeout_sec=0.02)

    def pose(self):
        for _ in range(200):
            self.spin_wall(0.05)
            if self.last is not None and self.sim_now() > 0:
                p = self.last.pose.pose
                return (p.position.x, p.position.y, yaw_of(p.orientation))
        raise RuntimeError("no odom")

    def drive(self, vx, vy, wz, dur=2.0):
        cmd = Twist()
        cmd.linear.x = vx
        cmd.linear.y = vy
        cmd.angular.z = wz
        t0 = self.sim_now()
        while self.sim_now() - t0 < dur:
            self.pub.publish(cmd)
            rclpy.spin_once(self, timeout_sec=0.02)
        for _ in range(10):
            self.pub.publish(Twist())
            rclpy.spin_once(self, timeout_sec=0.02)
        self.sim_sleep(0.4)


def main():
    rclpy.init()
    t = Tester()
    for _ in range(200):
        t.spin_wall(0.05)
        if t.sim_now() > 0:
            break
    t.sim_sleep(1.0)
    cases = [
        ("forward  vx=+0.20", 0.20, 0.0, 0.0),
        ("backward vx=-0.20", -0.20, 0.0, 0.0),
        ("left     vy=+0.20", 0.0, 0.20, 0.0),
        ("right    vy=-0.20", 0.0, -0.20, 0.0),
        ("rotate   wz=+0.50", 0.0, 0.0, 0.50),
        ("rotate   wz=-0.50", 0.0, 0.0, -0.50),
    ]
    for name, vx, vy, wz in cases:
        x0, y0, th0 = t.pose()
        t0 = t.sim_now()
        t.drive(vx, vy, wz, dur=2.0)
        x1, y1, th1 = t.pose()
        dt = max(1e-3, t.sim_now() - t0)
        dx, dy = x1 - x0, y1 - y0
        bx = math.cos(th0) * dx + math.sin(th0) * dy
        by = -math.sin(th0) * dx + math.cos(th0) * dy
        dth = math.atan2(math.sin(th1 - th0), math.cos(th1 - th0))
        print("%-20s simdt=%.2fs  vx=%+.3f  vy=%+.3f m/s  wz=%+.2f rad/s"
              % (name, dt, bx / dt, by / dt, dth / dt))
    t.destroy_node()
    rclpy.try_shutdown()


if __name__ == "__main__":
    main()
