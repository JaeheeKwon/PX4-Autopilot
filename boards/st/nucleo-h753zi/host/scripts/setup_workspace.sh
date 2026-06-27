#!/usr/bin/env bash
set -euo pipefail

workspace="${1:-${HOME}/nucleo_px4_ros2_ws}"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
host_dir="$(cd "${script_dir}/.." && pwd)"
repo_root="$(cd "${host_dir}/../../../.." && pwd)"
package_source="${host_dir}/ros2_ws/src/nucleo_px4_ros2_host"

if [[ ! -f /opt/ros/humble/setup.bash ]]; then
  echo "ROS 2 Humble was not found at /opt/ros/humble." >&2
  exit 1
fi

mkdir -p "${workspace}/src"

# Copy message definitions and the optional translation node from this exact
# firmware checkout. This avoids a px4_msgs/firmware schema mismatch.
"${repo_root}/Tools/copy_to_ros_ws.sh" "${workspace}"

package_link="${workspace}/src/nucleo_px4_ros2_host"
if [[ -L "${package_link}" ]]; then
  current_target="$(readlink -f "${package_link}")"
  expected_target="$(readlink -f "${package_source}")"
  if [[ "${current_target}" != "${expected_target}" ]]; then
    echo "Existing package symlink points elsewhere: ${package_link}" >&2
    exit 1
  fi
elif [[ -e "${package_link}" ]]; then
  echo "Workspace path already exists and is not a symlink: ${package_link}" >&2
  exit 1
else
  ln -s "${package_source}" "${package_link}"
fi

source /opt/ros/humble/setup.bash
cd "${workspace}"
rosdep install --from-paths src --ignore-src -y
colcon build --symlink-install

echo "Workspace ready: ${workspace}"
echo "Source it with: source ${workspace}/install/setup.bash"
