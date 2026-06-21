from glob import glob
from setuptools import setup

package_name = "nucleo_px4_ros2_ref"

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
    maintainer="PX4 Nucleo Reference",
    maintainer_email="px4-dev@example.invalid",
    description="Reference ROS 2 uXRCE-DDS monitor for PX4 on ST Nucleo-H753ZI.",
    license="BSD-3-Clause",
    entry_points={
        "console_scripts": [
            "bridge_health_monitor = nucleo_px4_ros2_ref.bridge_health_monitor:main",
        ],
    },
)

