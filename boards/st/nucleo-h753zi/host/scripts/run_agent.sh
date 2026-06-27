#!/usr/bin/env bash
set -euo pipefail

device="${1:-/dev/ttyUSB0}"
baud="${2:-921600}"

if ! command -v MicroXRCEAgent >/dev/null 2>&1; then
  echo "MicroXRCEAgent is not installed or not in PATH." >&2
  echo "For ROS 2 Humble, install Micro-XRCE-DDS-Agent v2.4.2." >&2
  exit 1
fi

if [[ ! -e "${device}" ]]; then
  echo "Serial device does not exist: ${device}" >&2
  echo "Inspect stable names with: ls -l /dev/serial/by-id/" >&2
  exit 1
fi

echo "Starting MicroXRCEAgent on ${device} at ${baud} baud"
exec MicroXRCEAgent serial --dev "${device}" -b "${baud}"
