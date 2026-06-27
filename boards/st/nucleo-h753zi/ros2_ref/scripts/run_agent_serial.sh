#!/usr/bin/env bash
set -euo pipefail

DEVICE="${1:-/dev/ttyUSB0}"
BAUD="${2:-921600}"

if ! command -v MicroXRCEAgent >/dev/null 2>&1; then
  echo "MicroXRCEAgent not found. Build and install eProsima Micro-XRCE-DDS-Agent v2.4.2 for ROS 2 Humble first." >&2
  exit 1
fi

if [ ! -e "${DEVICE}" ]; then
  echo "Serial device ${DEVICE} does not exist. Check dmesg for ttyUSB or ttyACM names." >&2
  exit 1
fi

echo "Starting MicroXRCEAgent on ${DEVICE} at ${BAUD} baud"
exec MicroXRCEAgent serial --dev "${DEVICE}" -b "${BAUD}"
