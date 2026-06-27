#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
host_dir="$(cd "${script_dir}/.." && pwd)"

for script in "${script_dir}"/*.sh; do
  bash -n "${script}"
done

python3 -B -c '
import ast
import pathlib
import sys
root = pathlib.Path(sys.argv[1])
files = list(root.rglob("*.py"))
for path in files:
    ast.parse(path.read_text(), filename=str(path))
print(f"Python syntax: {len(files)} files OK")
' "${host_dir}"

python3 -B -c '
import sys
import xml.etree.ElementTree as ET
ET.parse(sys.argv[1])
print("package.xml: OK")
' "${host_dir}/ros2_ws/src/nucleo_px4_ros2_host/package.xml"

echo "Host source checks passed without importing or building ROS 2."
