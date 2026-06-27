# ROS 2 and PX4 DDS Quick-Test Applications

This guide explains the three small Python applications in
`nucleo_px4_ros2_host` and how to use them to isolate connection problems.

## What each application tests

| Executable | What it does | Requires PX4? | Exit behavior |
|---|---|---:|---|
| `dds_test_talker` | Publishes numbered `std_msgs/String` messages through the selected ROS 2 DDS middleware. | No | Runs until Ctrl-C. |
| `dds_test_listener` | Waits for the expected string and verifies DDS discovery and delivery. | No | `0` on receipt, `1` on timeout or interruption. |
| `px4_dds_quick_test` | Receives PX4 status/time-sync topics and publishes a safe companion-computer heartbeat. | Yes | `0` when all checks pass, `1` on timeout or interruption. |

The local talker/listener pair tests ROS 2 and its DDS implementation only. It
does not use the Micro XRCE-DDS Agent. The PX4 test adds the XRCE client,
transport, agent, PX4 message definitions, and PX4 uORB/DDS endpoints.

## Safety

The PX4 test does not publish `VehicleCommand`, `OffboardControlMode`, actuator,
or trajectory-setpoint messages. It cannot arm the vehicle or command motion.
Its only outbound PX4 message is `/fmu/in/onboard_computer_status`.

Keep propellers removed whenever testing flight-controller hardware.

## One-time host setup

Requirements:

- Ubuntu 22.04 with ROS 2 Humble.
- Micro XRCE-DDS Agent 2.4.2 for the current Humble/PX4 configuration.
- This PX4 checkout available on the ROS 2 machine.

Create or refresh the workspace:

```sh
cd PX4-Autopilot
boards/st/nucleo-h753zi/host/scripts/setup_workspace.sh
```

The default workspace is `~/nucleo_px4_ros2_ws`. The setup script copies the
PX4 message definitions from this exact checkout, links the host package, runs
`rosdep`, and builds with `colcon --symlink-install`.

Rerun the setup script after adding or renaming a console application because
Python entry-point metadata is generated during the build.

For every terminal used below:

```sh
source /opt/ros/humble/setup.bash
source ~/nucleo_px4_ros2_ws/install/setup.bash
```

## Test 1: local ROS 2 DDS discovery

This is the first test to run. It separates ROS 2/DDS configuration problems
from UART, Micro XRCE-DDS, and PX4 problems.

Start the listener in terminal 1:

```sh
ros2 run nucleo_px4_ros2_host dds_test_listener
```

Start the talker within ten seconds in terminal 2:

```sh
ros2 run nucleo_px4_ros2_host dds_test_talker
```

Expected listener output resembles:

```text
[INFO] Waiting up to 10.0s for 'nucleo-dds-ok' on /nucleo/dds_quick_test
[INFO] PASS: received 'nucleo-dds-ok sequence=0'
```

The listener exits automatically with status 0. Stop the talker with Ctrl-C.
For scripts or CI, inspect the listener result with `echo $?`.

### Local-test parameters

```sh
ros2 run nucleo_px4_ros2_host dds_test_talker --ros-args \
  -p topic:=/lab/dds_test \
  -p message:=host-a-ok \
  -p rate_hz:=5.0

ros2 run nucleo_px4_ros2_host dds_test_listener --ros-args \
  -p topic:=/lab/dds_test \
  -p expected:=host-a-ok \
  -p timeout_sec:=20.0
```

Talker and listener must use the same topic, `ROS_DOMAIN_ID`, and compatible
`RMW_IMPLEMENTATION`. The applications may run on two machines if DDS discovery
and UDP traffic are permitted by the network.

## Test 2: physical Nucleo-H753ZI DDS connection

### 1. Connect USART6

Use a 3.3 V USB-UART adapter:

| Nucleo-H753ZI | Adapter |
|---|---|
| PG14 / CN12 pin 61, USART6 TX | RX |
| PG9 / CN11 pin 63, USART6 RX | TX |
| GND, for example CN12 pin 63 | GND |

Leave adapter VCC/5 V disconnected. No MB1364 jumper or solder-bridge change is
required for this USART6 route.

### 2. Start the serial agent

Use the stable adapter name shown under `/dev/serial/by-id/`:

```sh
ls -l /dev/serial/by-id/

boards/st/nucleo-h753zi/host/scripts/run_agent.sh \
  /dev/serial/by-id/<usb-uart-adapter>
```

The script starts:

```text
MicroXRCEAgent serial --dev <device> -b 921600
```

The agent should report creation of a client session and DDS entities after the
PX4 client connects.

### 3. Run the finite PX4 test

In another terminal:

```sh
boards/st/nucleo-h753zi/host/scripts/run_px4_quick_test.sh
```

The test waits up to 15 seconds for all of these conditions:

1. A `/fmu/out/vehicle_status_v4` sample is received.
2. A `/fmu/out/timesync_status` sample is received.
3. DDS discovers a PX4 reader for `/fmu/in/onboard_computer_status`.

Expected final output:

```text
[INFO] RX vehicle status: nav_state=..., arming_state=...
[INFO] RX time sync: round_trip_time=...us
[INFO] PASS: PX4 DDS outbound topics received and inbound reader matched
```

The reader match verifies the inbound DDS route through the agent. To verify
that a heartbeat reaches PX4 uORB, run this on the board's NSH console while the
test is active:

```text
nsh> listener onboard_computer_status -n 1
```

Useful board-side diagnostics are:

```text
nsh> uxrce_dds_client status
nsh> param show UXRCE_DDS_CFG
nsh> param show SER_TEL1_BAUD
```

## Test 3: PX4 SITL with SIH or Gazebo

SITL uses UDP instead of the physical UART. Start the agent first:

```sh
MicroXRCEAgent udp4 -p 8888
```

Start one simulator in another terminal:

```sh
# Fast, headless simulation
make px4_sitl_sih sihsim_quadx

# Or Gazebo
make px4_sitl gz_x500
```

Run the same host test in a third terminal:

```sh
boards/st/nucleo-h753zi/host/scripts/run_px4_quick_test.sh
```

This exercises the same ROS 2 application and PX4 DDS topics as the hardware
test while replacing serial transport with UDP.

## PX4 test parameters

The runner accepts positional arguments:

```text
run_px4_quick_test.sh [workspace] [px4_namespace] [timeout_sec] [status_topic]
```

Examples:

```sh
# Allow 30 seconds for a slow board startup
boards/st/nucleo-h753zi/host/scripts/run_px4_quick_test.sh \
  ~/nucleo_px4_ros2_ws "" 30

# Namespaced PX4 instance
boards/st/nucleo-h753zi/host/scripts/run_px4_quick_test.sh \
  ~/nucleo_px4_ros2_ws uav_0 20 /fmu/out/vehicle_status_v4
```

The equivalent direct ROS 2 command is:

```sh
ros2 run nucleo_px4_ros2_host px4_dds_quick_test --ros-args \
  -p px4_namespace:=uav_0 \
  -p timeout_sec:=20.0 \
  -p vehicle_status_topic:=/fmu/out/vehicle_status_v4
```

## Troubleshooting

| Symptom | Checks |
|---|---|
| `ros2 run` cannot find the executable | Rerun `setup_workspace.sh`, then source the workspace's `install/setup.bash` in the current terminal. |
| Local listener times out | Compare `ROS_DOMAIN_ID`, `RMW_IMPLEMENTATION`, and `ROS_LOCALHOST_ONLY` in both terminals. Check multicast/firewall policy when using two machines. |
| Agent shows no PX4 session | Check crossed TX/RX, common ground, 3.3 V logic, 921600 baud, serial permissions, and `uxrce_dds_client status`. |
| No `/fmu/out/*` topics | Confirm the agent session exists, then run `ros2 topic list | grep /fmu/`. Check that the agent version matches the ROS 2/PX4 DDS version. |
| Status works but time sync does not | Wait for synchronization and inspect `UXRCE_DDS_SYNCT` and `uxrce_dds_client status`. |
| PX4 test reports `inbound_readers=0` | Verify the namespace and that the firmware includes `/fmu/in/onboard_computer_status` in `dds_topics.yaml`. |
| ROS reports an incompatible message type | Rebuild the workspace with message definitions copied from the same PX4 checkout used to build the firmware. |
| `sensor_combined` or odometry is silent | This does not fail the quick test. Those topics may be silent without sensors, SIH, HITL, or a running estimator. |

## Source-only validation

On a development machine without ROS installed:

```sh
boards/st/nucleo-h753zi/host/scripts/check_source.sh
```

This checks Bash syntax, Python syntax, and `package.xml` parsing without
importing ROS packages or building the host workspace.
