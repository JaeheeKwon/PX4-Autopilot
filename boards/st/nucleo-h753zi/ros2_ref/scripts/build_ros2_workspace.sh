#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-${HOME}/nucleo_px4_ros2_ws}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REF_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PKG_SRC="${REF_ROOT}/ros2_ws/src/nucleo_px4_ros2_ref"

if [ ! -f /opt/ros/humble/setup.bash ]; then
  echo "ROS 2 Humble is not installed at /opt/ros/humble." >&2
  exit 1
fi

mkdir -p "${WORKSPACE}/src"

if [ ! -d "${WORKSPACE}/src/px4_msgs" ]; then
  git clone https://github.com/PX4/px4_msgs.git "${WORKSPACE}/src/px4_msgs"
fi

if [ ! -e "${WORKSPACE}/src/nucleo_px4_ros2_ref" ]; then
  ln -s "${PKG_SRC}" "${WORKSPACE}/src/nucleo_px4_ros2_ref"
fi

source /opt/ros/humble/setup.bash
cd "${WORKSPACE}"
rosdep install --from-paths src --ignore-src -y
colcon build --symlink-install

echo "Workspace built at ${WORKSPACE}"
echo "Source it with: source ${WORKSPACE}/install/setup.bash"

