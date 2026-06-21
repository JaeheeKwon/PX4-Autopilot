# Verification and Troubleshooting

Use this checklist after flashing firmware and wiring the serial DDS link.

## 1. Confirm PX4 Boot State

Open the ST-LINK console on CN1:

```sh
picocom -b 57600 /dev/ttyACM0
```

Check the DDS client module is present:

```text
nsh> uxrce_dds_client status
```

If it is not running and you are testing manually:

```text
nsh> uxrce_dds_client start -t serial -d /dev/ttyS1 -b 921600
```

If the command is unknown, rebuild with:

```text
CONFIG_MODULES_UXRCE_DDS_CLIENT=y
```

## 2. Confirm the Agent Connection

On the host:

```sh
boards/st/nucleo-h753zi/ros2_ref/scripts/run_agent_serial.sh /dev/ttyUSB0
```

Expected signs:

- The agent reports serial initialization success.
- The agent creates a session for client key `0x00000001`.
- PX4 logs show DDS data writers and readers being created.

If there is no session:

- Confirm CN10 D0 PG9 goes to adapter TX.
- Confirm CN10 D1 PG14 goes to adapter RX.
- Confirm board ground and adapter ground are connected.
- Confirm the adapter is 3.3 V logic.
- Confirm both sides use `921600` baud.
- Confirm no other process owns `/dev/ttyUSB0`.

## 3. List ROS 2 Topics

In a new host terminal:

```sh
source /opt/ros/humble/setup.bash
source ~/nucleo_px4_ros2_ws/install/setup.bash
ros2 topic list | grep /fmu
```

Expected examples:

```text
/fmu/out/vehicle_status
/fmu/out/vehicle_odometry
/fmu/out/sensor_combined
/fmu/out/timesync_status
```

If topics are missing:

- Check the agent terminal first.
- Check `uxrce_dds_client status` on PX4.
- Check that `px4_msgs` matches the firmware branch or local message set.
- If a namespace is configured, list with `ros2 topic list | grep uav_`.

## 4. Run the Reference Node

```sh
boards/st/nucleo-h753zi/ros2_ref/scripts/run_reference_node.sh
```

Expected output every few seconds:

```text
rx_hz vehicle_status=... vehicle_odometry=... sensor_combined=...
```

The node also publishes `/fmu/in/onboard_computer_status` at 1 Hz. On PX4:

```text
nsh> listener onboard_computer_status
```

If the listener never updates:

- Confirm `/fmu/in/onboard_computer_status` appears in `dds_topics.yaml`.
- Confirm the reference node is running in the same ROS domain as the agent.
- Confirm `ROS_DOMAIN_ID` is unset or matches `UXRCE_DDS_DOM_ID`.

## 5. QoS Checks

PX4 publishes most DDS topics as best-effort with transient-local durability.
Use the built-in topic tools with compatible QoS:

```sh
ros2 topic echo /fmu/out/vehicle_status \
  --qos-reliability best_effort \
  --qos-durability transient_local
```

For topics published from ROS 2 into PX4, best-effort and volatile durability
are the conservative defaults.

## 6. HITL Coexistence

The reference keeps DDS and MAVLink on separate physical links:

- MAVLink HITL: CN13 User USB, `/dev/ttyACM0` on PX4.
- DDS: USART6 CN10 D0/D1, `/dev/ttyS1` on PX4.

If HITL sensor data stops after enabling DDS, verify that DDS was not started
on `/dev/ttyACM0` and that the simulator still owns the CN13 MAVLink link.

