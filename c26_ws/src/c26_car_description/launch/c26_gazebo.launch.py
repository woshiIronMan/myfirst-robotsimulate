#!/usr/bin/env python3
"""启动 Gazebo Sim + C26 小车。

用法：
  ros2 launch c26_car_description c26_gazebo.launch.py              # 带 GUI
  ros2 launch c26_car_description c26_gazebo.launch.py headless:=true
  ros2 launch c26_car_description c26_gazebo.launch.py world:=<path.sdf>
"""
import os
from shlex import quote

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, IncludeLaunchDescription,
                            OpaqueFunction)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def launch_setup(context, *args, **kwargs):
    pkg = get_package_share_directory("c26_car_description")
    world = LaunchConfiguration("world").perform(context)
    headless = LaunchConfiguration("headless").perform(context).lower() in ("true", "1")
    robot_name = LaunchConfiguration("robot_name").perform(context)
    spawn_z = LaunchConfiguration("spawn_z").perform(context)
    drive = LaunchConfiguration("drive").perform(context).lower() in ("true", "1")
    planar = LaunchConfiguration("planar_drive").perform(context)
    planar_on = planar.lower() in ("true", "1")
    lidar = LaunchConfiguration("lidar").perform(context).lower() in ("true", "1")

    if not world or world == "default":
        world = os.path.join(pkg, "worlds", "c26_arena.sdf")

    xacro_file = os.path.join(pkg, "urdf", "c26_car.urdf.xacro")
    robot_description = ParameterValue(
        Command(["xacro ", quote(xacro_file),
                 " planar_drive:=", "true" if planar_on else "false",
                 " lidar:=", "true" if lidar else "false"]),
        value_type=str)

    gz_args = "-s " if headless else ""
    if headless and lidar:
        gz_args += "--headless-rendering "
    gz_args += "-r -v 3 " + quote(world)

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory("ros_gz_sim"),
                         "launch", "gz_sim.launch.py")),
        launch_arguments={"gz_args": gz_args}.items(),
    )

    rsp = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[{"robot_description": robot_description,
                     "use_sim_time": True}],
    )

    spawn = Node(
        package="ros_gz_sim",
        executable="create",
        output="screen",
        arguments=["-topic", "robot_description",
                   "-name", robot_name, "-z", spawn_z],
    )

    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        output="screen",
        parameters=[{"config_file": os.path.join(pkg, "config", "gz_bridge.yaml"),
                     "use_sim_time": True}],
    )

    nodes = [gz_sim, rsp, spawn, bridge]
    if lidar:
        nodes.extend([
            Node(package="ros_gz_bridge", executable="parameter_bridge",
                 name="c26_sensor_bridge", output="screen",
                 arguments=["/c26/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan",
                            "/model/c26/pose@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V"],
                 remappings=[("/c26/scan", "/scan"), ("/model/c26/pose", "/tf")],
                 parameters=[{"use_sim_time": True}]),
        ])

    if drive:
        nodes.append(Node(
            package="c26_car_description",
            executable="mecanum_drive.py",
            output="screen",
            parameters=[{"use_sim_time": True,
                         "drive_mode": "planar" if planar_on else "wheel"}],
        ))

    return nodes


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("world", default_value="default",
                              description="SDF world 文件路径"),
        DeclareLaunchArgument("headless", default_value="false",
                              description="true = 只跑服务器，不开 GUI"),
        DeclareLaunchArgument("robot_name", default_value="c26"),
        DeclareLaunchArgument("spawn_z", default_value="0.02"),
        DeclareLaunchArgument("drive", default_value="true",
                              description="是否启动 /cmd_vel 麦轮解算节点"),
        DeclareLaunchArgument("lidar", default_value="false",
                              description="启用二维激光雷达和里程计 TF"),
        DeclareLaunchArgument("planar_drive", default_value="true",
                              description="true = 整机平面速度驱动（横移/自转精确）；"
                                          "false = 纯轮子接触驱动"),
        OpaqueFunction(function=launch_setup),
    ])
