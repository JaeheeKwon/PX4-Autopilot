# Nucleo-H753ZI ROS 2 Host Application

This host application verifies the bidirectional PX4 uXRCE-DDS link without
arming the vehicle or publishing flight-control setpoints.

It:

- subscribes to PX4 status, odometry, sensor, and time-sync topics;
- reports receive rates and stale topics every two seconds; and
- publishes `/fmu/in/onboard_computer_status` at 1 Hz so the PX4-side inbound
  path can be checked with `listener onboard_computer_status`.

The default status topic is `/fmu/out/vehicle_status_v4`, which matches the
versioned `VehicleStatus` message in this PX4 branch.

## Prerequisites

- Ubuntu 22.04 and ROS 2 Humble
- Micro XRCE-DDS Agent v2.4.2
- A 3.3 V USB-UART adapter connected to USART6:
  - PG14 / CN12 pin 61 (board TX) to adapter RX
  - PG9 / CN11 pin 63 (board RX) to adapter TX
  - GND (for example CN12 pin 63) to adapter GND
  - Leave adapter VCC/5 V disconnected

The MB1364 Morpho headers are soldered by default and this USART6 route needs
no jumper or solder-bridge changes. PG14 is also Arduino D2; PG9 is not Arduino
D0. Do not use Arduino D0/D1, which are PB7/PB6 (LPUART1) on this board.

## Create and build the ROS workspace

Run this on the ROS 2 host, from the PX4 repository:

```sh
boards/st/nucleo-h753zi/host/scripts/setup_workspace.sh
```

The script creates `~/nucleo_px4_ros2_ws`, copies the exact message definitions
from this PX4 checkout, symlinks this package, resolves dependencies, and runs
`colcon build`.

This repository's PX4 build does not require ROS to be installed. The host
workspace is intentionally built only on the ROS machine.

Source-only checks can be run on a machine without ROS:

```sh
boards/st/nucleo-h753zi/host/scripts/check_source.sh
```

## Quick connection tests

See [QUICK_TESTS.md](QUICK_TESTS.md) for the complete application reference,
expected output, simulator workflow, parameters, exit codes, and troubleshooting.
For a clean-machine-to-acceptance procedure, use the
[ROS 2 integration test runbook](../docs/ros2/ros2_integration_test_runbook.html).

### Test ROS 2 and DDS locally

This pair checks DDS participant discovery and message delivery without PX4.
Run the listener first so its ten-second timeout does not expire during setup.

Terminal 1:

```sh
source /opt/ros/humble/setup.bash
source ~/nucleo_px4_ros2_ws/install/setup.bash
ros2 run nucleo_px4_ros2_host dds_test_listener
```

Terminal 2:

```sh
source /opt/ros/humble/setup.bash
source ~/nucleo_px4_ros2_ws/install/setup.bash
ros2 run nucleo_px4_ros2_host dds_test_talker
```

The listener exits with status 0 after receiving a message containing
`nucleo-dds-ok`, or status 1 after its timeout. Both processes must use the same
`ROS_DOMAIN_ID` and compatible `RMW_IMPLEMENTATION` settings.

### Test the PX4 uXRCE-DDS connection

Start the serial agent for the physical board, or a UDP agent for PX4 SITL:

```sh
# Physical Nucleo-H753ZI
boards/st/nucleo-h753zi/host/scripts/run_agent.sh \
  /dev/serial/by-id/<usb-uart-adapter>

# PX4 SITL/SIH/Gazebo alternative
MicroXRCEAgent udp4 -p 8888
```

Then run the finite smoke test:

```sh
boards/st/nucleo-h753zi/host/scripts/run_px4_quick_test.sh
```

It exits successfully after receiving `vehicle_status_v4` and `timesync_status`
and discovering the PX4 reader for `onboard_computer_status`. It publishes only
the non-commanding companion-computer status message; it never arms the vehicle
or sends control setpoints. To prove delivery all the way to PX4 uORB, run this
on the NSH console while the test is active:

```text
listener onboard_computer_status -n 1
```

Namespace, timeout, and status-topic overrides are positional:

```sh
boards/st/nucleo-h753zi/host/scripts/run_px4_quick_test.sh \
  ~/nucleo_px4_ros2_ws uav_0 20 /fmu/out/vehicle_status_v4
```

## Run

Terminal 1:

```sh
boards/st/nucleo-h753zi/host/scripts/run_agent.sh \
  /dev/serial/by-id/<usb-uart-adapter>
```

Terminal 2:

```sh
boards/st/nucleo-h753zi/host/scripts/run_monitor.sh
```

Optional namespace and status topic overrides:

```sh
boards/st/nucleo-h753zi/host/scripts/run_monitor.sh \
  ~/nucleo_px4_ros2_ws uav_0 /fmu/out/vehicle_status_v4
```

On the PX4 NSH console:

```text
uxrce_dds_client status
listener onboard_computer_status -n 5
```

With no HITL simulator or real sensors, `sensor_combined` and odometry can be
silent. `timesync_status` and `vehicle_status_v4` are the initial outbound
transport checks.
