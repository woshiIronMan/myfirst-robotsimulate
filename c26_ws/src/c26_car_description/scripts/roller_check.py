#!/usr/bin/env python3
"""检查滚子关节是否真的在自由自转（麦轮能否横移的关键）。"""
import time

import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from geometry_msgs.msg import Twist
from sensor_msgs.msg import JointState


class Check(Node):
    def __init__(self):
        super().__init__("roller_check")
        self.set_parameters([Parameter("use_sim_time", Parameter.Type.BOOL, True)])
        self.pub = self.create_publisher(Twist, "/cmd_vel", 10)
        self.js = None
        self.create_subscription(JointState, "/joint_states", self.cb, 10)

    def cb(self, m):
        self.js = m

    def run(self, vx, vy, wz, dur=2.0):
        cmd = Twist()
        cmd.linear.x = vx
        cmd.linear.y = vy
        cmd.angular.z = wz
        t0 = time.time()
        while time.time() - t0 < dur:
            self.pub.publish(cmd)
            rclpy.spin_once(self, timeout_sec=0.02)
        rclpy.spin_once(self, timeout_sec=0.05)
        if self.js is None:
            print("no joint_states")
            return
        names, vels = self.js.name, self.js.velocity
        out = []
        for n, v in zip(names, vels):
            if n.endswith("_joint") and "roller" not in n:
                out.append("%s=%+.2f" % (n.replace("_joint", ""), v))
        roll = [abs(v) for n, v in zip(names, vels) if "roller" in n]
        print("cmd(vx=%.2f vy=%.2f wz=%.2f)" % (vx, vy, wz))
        print("   wheel joint vel : " + "  ".join(out))
        if roll:
            print("   roller |vel| max=%.1f  mean=%.1f rad/s  (n=%d)"
                  % (max(roll), sum(roll) / len(roll), len(roll)))


def main():
    rclpy.init()
    c = Check()
    t0 = time.time()
    while time.time() - t0 < 8:
        rclpy.spin_once(c, timeout_sec=0.1)
        if c.js is not None:
            break
    c.run(0.20, 0.0, 0.0)
    c.run(0.0, 0.20, 0.0)
    c.run(0.0, 0.0, 0.50)
    c.destroy_node()
    rclpy.try_shutdown()


if __name__ == "__main__":
    main()
