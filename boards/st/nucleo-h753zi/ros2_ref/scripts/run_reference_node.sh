#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-${HOME}/nucleo_px4_ros2_ws}"
PX4_NAMESPACE="${2:-}"

if [ ! -f /opt/ros/humble/setup.bash ]; then
  echo "ROS 2 Humble is not installed at /opt/ros/humble." >&2
  exit 1
fi

if [ ! -f "${WORKSPACE}/install/setup.bash" ]; then
  echo "Workspace ${WORKSPACE} is not built. Run scripts/build_ros2_workspace.sh first." >&2
  exit 1
fi

source /opt/ros/humble/setup.bash
source "${WORKSPACE}/install/setup.bash"

exec ros2 run nucleo_px4_ros2_ref bridge_health_monitor \
  --ros-args -p px4_namespace:="${PX4_NAMESPACE}"

