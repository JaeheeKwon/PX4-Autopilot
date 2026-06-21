from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    px4_namespace = LaunchConfiguration("px4_namespace")

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "px4_namespace",
                default_value="",
                description="Optional PX4 DDS namespace, for example uav_0.",
            ),
            Node(
                package="nucleo_px4_ros2_ref",
                executable="bridge_health_monitor",
                name="nucleo_bridge_health_monitor",
                output="screen",
                parameters=[{"px4_namespace": px4_namespace}],
            ),
        ]
    )

