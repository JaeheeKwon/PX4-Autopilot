# Nucleo-H753ZI ROS 2 / DDS Reference

This directory contains a board-specific reference for using PX4 on the
ST Nucleo-H753ZI with ROS 2 over uXRCE-DDS.

The flight controller does not run full ROS 2 nodes. PX4 runs the lightweight
`uxrce_dds_client` module on the board. A host or companion computer runs the
Micro XRCE-DDS Agent, and ROS 2 nodes communicate through that agent using
PX4 `px4_msgs` topics.

## Reference Layout

| Path | Purpose |
|---|---|
| `index.html` | Top-level HTML entry point |
| `docs/index.html` | Rendered HTML documentation index with diagrams |
| `docs/host_setup_ubuntu_22_04.md` | Ubuntu 22.04 and ROS 2 Humble host setup |
| `docs/host_setup_ubuntu_22_04.html` | HTML host setup guide with setup flow diagram |
| `docs/board_integration.md` | Nucleo-H753ZI wiring, firmware, and PX4 startup integration |
| `docs/board_integration.html` | HTML board integration guide with architecture and wiring diagrams |
| `docs/verification.md` | Bring-up checks and troubleshooting |
| `docs/verification.html` | HTML verification guide with bring-up flow diagram |
| `config/rc.board_extras` | Optional PX4 startup hook to auto-start `uxrce_dds_client` on USART6 |
| `scripts/run_agent_serial.sh` | Host helper for the serial Micro XRCE-DDS Agent |
| `scripts/build_ros2_workspace.sh` | Host helper to build a ROS 2 workspace with this reference app |
| `scripts/run_reference_node.sh` | Host helper to run the reference ROS 2 node |
| `ros2_ws/src/nucleo_px4_ros2_ref` | Reference ROS 2 Python package |

## Board-Specific Topology

The Nucleo-H753ZI reference keeps the existing HITL MAVLink link on USB CN13
and uses USART6 for ROS 2 / DDS:

| Function | Board connector | PX4 device | Host side |
|---|---|---|---|
| NSH console | CN1 ST-LINK USB | `/dev/ttyS0` | USB CDC serial at 57600 baud |
| MAVLink HITL / QGC | CN13 User USB | `/dev/ttyACM0` | USB CDC MAVLink |
| ROS 2 / uXRCE-DDS | USART6 on Morpho headers | `/dev/ttyS1` | USB-UART adapter at 921600 baud |

USART6 wiring:

| Nucleo header | MCU pin | Signal | USB-UART adapter |
|---|---|---|---|
| CN11 pin 63 | PG9 | USART6 RX | TX |
| CN12 pin 61 | PG14 | USART6 TX | RX |
| GND | GND | Ground | GND |

Use a 3.3 V USB-UART adapter. Do not connect a 5 V UART signal to the STM32 pins.

## Quick Start

For the rendered documentation, open:

```text
boards/st/nucleo-h753zi/ros2_ref/index.html
```

1. Set up the Ubuntu 22.04 host:

   ```sh
   less boards/st/nucleo-h753zi/ros2_ref/docs/host_setup_ubuntu_22_04.md
   ```

2. DDS auto-start is already configured through TEL1, `UXRCE_DDS_CFG=101`,
   and `SER_TEL1_BAUD=921600`. Do not install a second startup hook.

3. Build and flash the board:

   ```sh
   make st_nucleo-h753zi_default
   make st_nucleo-h753zi_default upload
   ```

4. Start the Micro XRCE-DDS Agent on the host:

   ```sh
   boards/st/nucleo-h753zi/ros2_ref/scripts/run_agent_serial.sh /dev/ttyUSB0
   ```

5. Build the ROS 2 reference workspace:

   ```sh
   boards/st/nucleo-h753zi/ros2_ref/scripts/build_ros2_workspace.sh
   ```

6. Run the reference node:

   ```sh
   boards/st/nucleo-h753zi/ros2_ref/scripts/run_reference_node.sh
   ```

The node subscribes to PX4 output topics such as `/fmu/out/vehicle_status`,
`/fmu/out/vehicle_odometry`, and `/fmu/out/sensor_combined`. It also publishes
`/fmu/in/onboard_computer_status` at 1 Hz to verify the ROS 2 to PX4 direction
without arming the vehicle or sending control setpoints.

## Safety

This reference intentionally avoids `VehicleCommand`, `OffboardControlMode`,
`TrajectorySetpoint`, and direct actuator publishers. Use it first to validate
transport, message compatibility, and timing. Add offboard control only after
the bridge is stable and the board is connected to a simulator or a physically
safe test setup.
