"""启动室内场景和 AMCL / Nav2，或启动 SLAM Toolbox 进行建图。"""
from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, GroupAction, IncludeLaunchDescription,
                            OpaqueFunction, SetEnvironmentVariable)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def setup(context):
    package = Path(get_package_share_directory("c26_car_description"))
    mode = LaunchConfiguration("mode").perform(context)
    nav2_params = str(package / "config/c26_nav2.yaml")
    sim_time = {"use_sim_time": True}
    actions = [GroupAction([
        SetEnvironmentVariable("LIBGL_ALWAYS_SOFTWARE", "1"),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(str(package / "launch/c26_gazebo.launch.py")),
            launch_arguments={"headless": "true", "lidar": "true",
                              "world": str(package / "worlds/c26_indoor.sdf")}.items(),
        ),
    ])]
    if mode == "mapping":
        slam = Path(get_package_share_directory("slam_toolbox"))
        actions.append(IncludeLaunchDescription(
            PythonLaunchDescriptionSource(str(slam / "launch/online_async_launch.py")),
            launch_arguments={"use_sim_time": "true", "slam_params_file":
                              str(package / "config/c26_slam.yaml")}.items(),
        ))
    else:
        servers = [
            ("nav2_map_server", "map_server"),
            ("nav2_amcl", "amcl"),
            ("nav2_planner", "planner_server"),
            ("nav2_controller", "controller_server"),
            ("nav2_behaviors", "behavior_server"),
            ("nav2_bt_navigator", "bt_navigator"),
        ]
        for node_package, name in servers:
            parameters = [nav2_params, sim_time]
            if name == "map_server":
                parameters.append({"yaml_filename": LaunchConfiguration("map")})
            actions.append(Node(package=node_package, executable=name, name=name,
                                parameters=parameters, output="screen"))
        actions.append(Node(
            package="nav2_lifecycle_manager", executable="lifecycle_manager",
            name="lifecycle_manager_nav2", output="screen",
            parameters=[sim_time, {"autostart": True,
                                  "node_names": [name for _, name in servers]}],
        ))
    rviz_config = package / "config/c26_navigation.rviz"
    actions.append(Node(package="rviz2", executable="rviz2", output="screen",
                        arguments=["-d", str(rviz_config)], parameters=[sim_time],
                        additional_env={"QT_QPA_PLATFORM": "xcb",
                                        "QT_XCB_GL_INTEGRATION": "xcb_glx",
                                        "LIBGL_ALWAYS_SOFTWARE": "1"},
                        condition=IfCondition(LaunchConfiguration("rviz"))))
    return actions


def generate_launch_description():
    package = Path(get_package_share_directory("c26_car_description"))
    return LaunchDescription([
        DeclareLaunchArgument("mode", default_value="navigation", choices=["mapping", "navigation"]),
        DeclareLaunchArgument("map", default_value=str(package / "maps/c26_indoor.yaml")),
        DeclareLaunchArgument("rviz", default_value="false"),
        # Keep Fast DDS discovery and lifecycle bonds off stale shared-memory ports.
        SetEnvironmentVariable("FASTDDS_BUILTIN_TRANSPORTS", "UDPv4"),
        OpaqueFunction(function=setup),
    ])
