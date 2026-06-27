#!/usr/bin/env bash
set -euo pipefail

workspace="${1:-${HOME}/nucleo_px4_ros2_ws}"
px4_namespace="${2:-}"
timeout_sec="${3:-15}"
vehicle_status_topic="${4:-/fmu/out/vehicle_status_v4}"

if [[ ! -f /opt/ros/humble/setup.bash ]]; then
  echo "ROS 2 Humble was not found at /opt/ros/humble." >&2
  exit 1
fi

if [[ ! -f "${workspace}/install/setup.bash" ]]; then
  echo "ROS workspace is not built: ${workspace}" >&2
  echo "Run boards/st/nucleo-h753zi/host/scripts/setup_workspace.sh first." >&2
  exit 1
fi

source /opt/ros/humble/setup.bash
source "${workspace}/install/setup.bash"

exec ros2 run nucleo_px4_ros2_host px4_dds_quick_test --ros-args \
  -p px4_namespace:="${px4_namespace}" \
  -p timeout_sec:="${timeout_sec}" \
  -p vehicle_status_topic:="${vehicle_status_topic}"
