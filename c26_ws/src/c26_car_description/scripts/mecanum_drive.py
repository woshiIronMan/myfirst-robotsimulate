#!/usr/bin/env python3
"""把 /cmd_vel (geometry_msgs/Twist) 解算成 4 个麦轮的转速命令。

麦轮逆运动学（X 型布置，vx 前进 / vy 左移 / wz 逆时针）：
    w_fl = ( vx - vy - (Lx+Ly)*wz ) / r
    w_fr = ( vx + vy + (Lx+Ly)*wz ) / r
    w_rl = ( vx + vy - (Lx+Ly)*wz ) / r
    w_rr = ( vx - vy + (Lx+Ly)*wz ) / r
其中 Lx = 轴距/2，Ly = 轮距/2，r = 轮半径。

如果实测方向相反，用参数 invert_<wheel> 或全局 invert_all 修正。
"""
import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64


WHEELS = ["wheel_fl", "wheel_fr", "wheel_rl", "wheel_rr"]


class MecanumDrive(Node):
    def __init__(self):
        super().__init__("mecanum_drive")

        self.declare_parameter("wheel_radius", 0.0325)
        self.declare_parameter("wheel_base", 0.210)   # 前后轮轴距 (m)
        self.declare_parameter("track_width", 0.207)  # 左右轮距 (m)
        self.declare_parameter("cmd_timeout", 0.5)    # 秒，超时停车
        self.declare_parameter("max_wheel_speed", 45.0)  # rad/s
        self.declare_parameter("invert_all", False)
        self.declare_parameter("yaw_sign", -1.0)   # 标定值：仿真中转向方向与解算符号相反
        self.declare_parameter("invert_fl", False)
        self.declare_parameter("invert_fr", False)
        self.declare_parameter("invert_rl", False)
        self.declare_parameter("invert_rr", False)
        # wheel : 只驱动轮子（真实接触，前进/后退可靠，横移弱）
        # planar: 轮子照常转（视觉）+ 由 Gazebo 直接给车体平面速度（横移/自转精确）
        self.declare_parameter("drive_mode", "planar")
        self.drive_mode = str(self.get_parameter("drive_mode").value)

        r = float(self.get_parameter("wheel_radius").value)
        self.half_k = 0.5 * (float(self.get_parameter("wheel_base").value)
                             + float(self.get_parameter("track_width").value))
        # 仿真里滚子接触导致的转向效率/方向修正（实测标定，见 README）
        self.yaw_k = self.half_k * float(self.get_parameter("yaw_sign").value)
        self.r = r
        self.cmd_timeout = float(self.get_parameter("cmd_timeout").value)
        self.max_w = float(self.get_parameter("max_wheel_speed").value)

        signs = {}
        inv_all = bool(self.get_parameter("invert_all").value)
        for w in WHEELS:
            s = -1.0 if bool(self.get_parameter("invert_" + w.split("_")[1]).value) else 1.0
            signs[w] = s * (-1.0 if inv_all else 1.0)

        self.pubs = {
            w: self.create_publisher(Float64, "/c26/cmd_vel_wheel/" + w, 10)
            for w in WHEELS
        }

        # planar 模式下由 Gazebo VelocityControl 直接执行整机平面速度
        self.planar_pub = self.create_publisher(Twist, "/cmd_vel_planar", 10)

        self.create_subscription(Twist, "/cmd_vel", self.on_cmd, 10)
        self.last_cmd_time = self.get_clock().now()
        self.last = [0.0, 0.0, 0.0]
        self.signs = signs
        self.create_timer(0.02, self.tick)  # 50 Hz
        self.get_logger().info(
            "mecanum_drive ready: mode=%s r=%.4f m, K=(Lx+Ly)=%.4f m"
            % (self.drive_mode, r, self.half_k))

    def on_cmd(self, msg: Twist):
        self.last = [msg.linear.x, msg.linear.y, msg.angular.z]
        self.last_cmd_time = self.get_clock().now()
        self.publish_wheels(*self.last)

    def publish_wheels(self, vx, vy, wz):
        k = self.yaw_k
        speeds = {
            "wheel_fl": (vx - vy - k * wz) / self.r,
            "wheel_fr": (vx + vy + k * wz) / self.r,
            "wheel_rl": (vx + vy - k * wz) / self.r,
            "wheel_rr": (vx - vy + k * wz) / self.r,
        }
        for w in WHEELS:
            w_val = speeds[w] * self.signs[w]
            w_val = max(-self.max_w, min(self.max_w, w_val))
            self.pubs[w].publish(Float64(data=float(w_val)))

        # planar 模式：把整车平面速度直接交给 Gazebo（横移/自转精确）
        if self.drive_mode == "planar":
            t = Twist()
            t.linear.x = float(vx)
            t.linear.y = float(vy)
            t.angular.z = float(wz)
            self.planar_pub.publish(t)

    def tick(self):
        dt = (self.get_clock().now() - self.last_cmd_time).nanoseconds * 1e-9
        if dt > self.cmd_timeout:
            self.publish_wheels(0.0, 0.0, 0.0)
        else:
            self.publish_wheels(*self.last)


def main():
    rclpy.init()
    node = MecanumDrive()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
