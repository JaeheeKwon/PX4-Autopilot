from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument("px4_namespace", default_value=""),
            DeclareLaunchArgument(
                "vehicle_status_topic",
                default_value="/fmu/out/vehicle_status_v4",
            ),
            Node(
                package="nucleo_px4_ros2_host",
                executable="bridge_health_monitor",
                name="nucleo_px4_bridge_health",
                output="screen",
                parameters=[
                    {"px4_namespace": LaunchConfiguration("px4_namespace")},
                    {
                        "vehicle_status_topic": LaunchConfiguration(
                            "vehicle_status_topic"
                        )
                    },
                ],
            ),
        ]
    )
