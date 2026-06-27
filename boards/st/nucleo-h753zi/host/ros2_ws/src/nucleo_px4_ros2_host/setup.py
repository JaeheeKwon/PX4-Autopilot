from glob import glob

from setuptools import setup


package_name = "nucleo_px4_ros2_host"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", glob("launch/*.launch.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="PX4 Nucleo-H753ZI Developers",
    maintainer_email="px4-dev@example.invalid",
    description="Safe ROS 2 bridge monitor for PX4 on Nucleo-H753ZI.",
    license="BSD-3-Clause",
    entry_points={
        "console_scripts": [
            "bridge_health_monitor = nucleo_px4_ros2_host.bridge_health_monitor:main",
            "dds_test_talker = nucleo_px4_ros2_host.dds_test_talker:main",
            "dds_test_listener = nucleo_px4_ros2_host.dds_test_listener:main",
            "px4_dds_quick_test = nucleo_px4_ros2_host.px4_dds_quick_test:main",
        ],
    },
)
