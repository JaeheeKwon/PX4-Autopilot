# PX4 Zenoh Host Test Tool

A standalone Python test tool for the Nucleo-H753ZI Zenoh integration.
Decodes raw CDR payloads from PX4 uORB topics over Zenoh without requiring
ROS 2 or `px4_msgs`.

## Requirements

Python 3.10 or later.

```sh
pip install -r requirements.txt
# or directly:
pip install "eclipse-zenoh>=1.0.0"
```

## Modes

### `monitor` — live terminal dashboard

Subscribes to `vehicle_attitude`, `sensor_combined`, `vehicle_local_position`,
`vehicle_status`, and `battery_status` simultaneously and renders a live
refreshing terminal display.

```sh
# Connect to a zenohd router on the host
python3 px4_zenoh_monitor.py monitor --router tcp/192.168.0.1:7447

# Multicast peer discovery (no router, board and host on same subnet)
python3 px4_zenoh_monitor.py monitor --peer udp/224.0.0.224:7446
```

Example output:

```
╔══════════════════════════════════════════════════════╗
║        PX4 Nucleo-H753ZI  ·  Zenoh Monitor           ║
╚══════════════════════════════════════════════════════╝
  Last message: 0.1s ago   msgs: att=312 imu=312 pos=62 stat=4 batt=4

  ── Vehicle Status ─────────────────────────────────
  Arming   : DISARMED
  Nav mode : MANUAL

  ── Attitude (roll / pitch / yaw) ───────────────────
  Roll  :    1.23 °
  Pitch :   -0.45 °
  Yaw   :   92.10 °
  q     : [ 0.9997   0.0107  -0.0039   0.8034]

  ── Local Position (NED) ────────────────────────────
  xy_valid=NO   z_valid=NO   v_xy_valid=NO   v_z_valid=NO
  x=     nan m   y=     nan m   alt=     nan m
  vx=    nan m/s   vy=    nan m/s   vz=    nan m/s

  ── IMU (sensor_combined) ───────────────────────────
  gyro  :   0.001    0.002   -0.001  rad/s
  accel :   0.034   -0.012    9.807  m/s²

  ── Battery ─────────────────────────────────────────
  (not connected)
```

### `echo` — print individual messages

Prints every decoded field of each received message for one topic.

```sh
python3 px4_zenoh_monitor.py echo vehicle_attitude --router tcp/192.168.0.1:7447
python3 px4_zenoh_monitor.py echo sensor_combined  --router tcp/192.168.0.1:7447
python3 px4_zenoh_monitor.py echo vehicle_status   --router tcp/192.168.0.1:7447
```

Available topics:

| Name | PX4 key expression |
|---|---|
| `vehicle_attitude` | `0/fmu/out/vehicle_attitude/**` |
| `sensor_combined` | `0/fmu/out/sensor_combined/**` |
| `vehicle_local_position` | `0/fmu/out/vehicle_local_position/**` |
| `vehicle_status` | `0/fmu/out/vehicle_status/**` |
| `battery_status` | `0/fmu/out/battery_status/**` |

### `offboard` — trajectory setpoint publisher

Publishes `offboard_control_mode` + `trajectory_setpoint` at 20 Hz.
Useful for testing the Zenoh subscriber path from host → PX4.

> **Safety**: the vehicle must be armed and OFFBOARD mode engaged externally
> (e.g. via RC switch) before the setpoints take effect. This tool sends
> setpoints continuously; kill it with Ctrl+C before disarming.

```sh
# Hold position at (x=0, y=0, z=-2) metres in NED (2 m above home, north/east aligned)
python3 px4_zenoh_monitor.py offboard \
    --router tcp/192.168.0.1:7447 \
    --pos 0.0 0.0 -2.0 \
    --yaw 0.0

# Velocity setpoint: drift north at 0.5 m/s
python3 px4_zenoh_monitor.py offboard \
    --router tcp/192.168.0.1:7447 \
    --vel 0.5 0.0 0.0
```

## CDR decoding notes

PX4 serialises uORB messages using CycloneDDS CDR v1 (little-endian) with
a 4-byte ROS 2 header `\x00\x01\x00\x00`.  Fields are serialised in .msg
file order with natural alignment (uint64 → 8, float32/uint32 → 4, uint8/bool
→ 1).  Padding bytes are inserted before each field to satisfy its alignment
requirement.

`CDRDecoder` in `px4_zenoh_monitor.py` implements this automatically — calling
`d.float32()` after `d.uint8()` inserts up to 3 padding bytes as needed, so
the decoder call sequence simply mirrors the .msg field order.

## Key expression format

PX4 publishes on key expressions of the form:

```
<domain_id>/fmu/<dir>/<topic>/rt/<CamelCaseType>_/RIHS01_<32-byte-hash>
```

The `**` wildcard in subscriptions matches the `/rt/…` suffix, so you do not
need to know the type hash to receive messages.  The domain ID defaults to `0`
and must match the `ZENOH_DOMAIN_ID` parameter on the board.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `ImportError: No module named 'zenoh'` | `pip install eclipse-zenoh` |
| No messages received | Check `zenohd` is running on `--router` address; verify board shows `Connected` in `zenoh status` |
| `CDR buffer underflow` errors | Topic field layout mismatch — check the board firmware was built from the same PX4 source as this tool |
| All values `nan` | EKF2 not initialised — normal until IMU converges; local position requires GPS lock |
| `offboard` mode not engaging | Arm the vehicle and switch to OFFBOARD via RC or GCS before running this tool |
