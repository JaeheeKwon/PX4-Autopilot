#!/usr/bin/env python3
"""
PX4 Zenoh host-side test tool for Nucleo-H753ZI.

Connects directly to a running zenohd (or peers via multicast) and decodes
raw CDR payloads from PX4 uORB topics.  No ROS 2 or px4_msgs installation
required.

Usage
-----
    # Live dashboard (vehicle_attitude, sensor_combined, local_position, status, battery)
    python3 px4_zenoh_monitor.py monitor --router tcp/192.168.0.1:7447

    # Print every message on one topic
    python3 px4_zenoh_monitor.py echo vehicle_attitude --router tcp/192.168.0.1:7447

    # Send trajectory_setpoint + offboard_control_mode (offboard control test)
    python3 px4_zenoh_monitor.py offboard --router tcp/192.168.0.1:7447 \
        --pos 0.0 0.0 -2.0 --yaw 0.0

    # Multicast peer mode (no router needed)
    python3 px4_zenoh_monitor.py monitor --peer udp/224.0.0.224:7446

Requirements
------------
    pip install eclipse-zenoh>=1.0.0
"""

from __future__ import annotations

import argparse
import math
import struct
import sys
import time
import threading
from typing import Any, Dict, Optional

# ---------------------------------------------------------------------------
# Zenoh import
# ---------------------------------------------------------------------------
try:
    import zenoh
except ImportError:
    print("ERROR: eclipse-zenoh not installed.  Run:  pip install eclipse-zenoh", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# CDR codec
# ---------------------------------------------------------------------------

class CDRDecoder:
    """
    Minimal CDR v1 / XCDR v1 decoder (little-endian).

    The 4-byte ROS 2 CDR header is consumed automatically.
    Alignment is computed relative to the start of the CDR payload
    (i.e., after the header), matching the behaviour of CycloneDDS
    dds_cdrstream when m_buffer points past the header and m_index=0.
    """

    def __init__(self, raw: bytes):
        if len(raw) < 4:
            raise ValueError(f"CDR payload too short: {len(raw)} bytes")
        # Verify little-endian marker (byte 1 bit 0 = 1).  Be lenient.
        self._buf = raw[4:]
        self._pos = 0

    # -- alignment ----------------------------------------------------------

    def _align(self, n: int) -> None:
        rem = self._pos % n
        if rem:
            self._pos += n - rem

    def _check(self, n: int) -> None:
        if self._pos + n > len(self._buf):
            raise ValueError(
                f"CDR buffer underflow: need {n} bytes at pos {self._pos}, "
                f"have {len(self._buf) - self._pos}"
            )

    # -- primitives ---------------------------------------------------------

    def bool_(self) -> bool:
        self._check(1)
        v = self._buf[self._pos] != 0
        self._pos += 1
        return v

    def uint8(self) -> int:
        self._check(1)
        v = self._buf[self._pos]
        self._pos += 1
        return v

    def int16(self) -> int:
        self._align(2)
        self._check(2)
        v, = struct.unpack_from("<h", self._buf, self._pos)
        self._pos += 2
        return v

    def uint16(self) -> int:
        self._align(2)
        self._check(2)
        v, = struct.unpack_from("<H", self._buf, self._pos)
        self._pos += 2
        return v

    def int32(self) -> int:
        self._align(4)
        self._check(4)
        v, = struct.unpack_from("<i", self._buf, self._pos)
        self._pos += 4
        return v

    def uint32(self) -> int:
        self._align(4)
        self._check(4)
        v, = struct.unpack_from("<I", self._buf, self._pos)
        self._pos += 4
        return v

    def uint64(self) -> int:
        self._align(8)
        self._check(8)
        v, = struct.unpack_from("<Q", self._buf, self._pos)
        self._pos += 8
        return v

    def float32(self) -> float:
        self._align(4)
        self._check(4)
        v, = struct.unpack_from("<f", self._buf, self._pos)
        self._pos += 4
        return v

    def float64(self) -> float:
        self._align(8)
        self._check(8)
        v, = struct.unpack_from("<d", self._buf, self._pos)
        self._pos += 8
        return v

    def float32_array(self, n: int) -> list[float]:
        self._align(4)
        self._check(4 * n)
        v = list(struct.unpack_from(f"<{n}f", self._buf, self._pos))
        self._pos += 4 * n
        return v

    def skip(self, n: int) -> None:
        """Skip exactly n bytes (no alignment applied)."""
        self._pos += n

    def skip_to(self, pos: int) -> None:
        """Skip to an absolute byte position within the CDR payload."""
        self._pos = pos


class CDREncoder:
    """
    Minimal CDR v1 encoder (little-endian).
    Prepends the 4-byte ROS 2 CDR header automatically.
    """

    _HEADER = b"\x00\x01\x00\x00"

    def __init__(self):
        self._buf = bytearray()

    def _align(self, n: int) -> None:
        rem = len(self._buf) % n
        if rem:
            self._buf += b"\x00" * (n - rem)

    def bool_(self, v: bool) -> "CDREncoder":
        self._buf += struct.pack("B", int(bool(v)))
        return self

    def uint8(self, v: int) -> "CDREncoder":
        self._buf += struct.pack("B", v & 0xFF)
        return self

    def uint64(self, v: int) -> "CDREncoder":
        self._align(8)
        self._buf += struct.pack("<Q", v)
        return self

    def float32(self, v: float) -> "CDREncoder":
        self._align(4)
        self._buf += struct.pack("<f", v)
        return self

    def float32_array(self, arr: list[float]) -> "CDREncoder":
        self._align(4)
        self._buf += struct.pack(f"<{len(arr)}f", *arr)
        return self

    def build(self) -> bytes:
        return self._HEADER + bytes(self._buf)


# ---------------------------------------------------------------------------
# Zenoh key expression helpers
# ---------------------------------------------------------------------------

DOMAIN = 0          # must match ZENOH_DOMAIN_ID param on the board
_TOPIC_ROOT = f"{DOMAIN}/fmu"


def sub_keyexpr(fmu_path: str) -> str:
    """
    Wildcard key expression that matches any type-hash suffix.
    E.g. sub_keyexpr('out/sensor_combined') →
         '0/fmu/out/sensor_combined/**'
    """
    return f"{_TOPIC_ROOT}/{fmu_path}/**"


def pub_keyexpr(fmu_path: str, type_name: str) -> str:
    """
    Key expression for publishing without a type hash (TypeHashNotSupported).
    Compatible with PX4 when CONFIG_ZENOH_KEY_TYPE_HASH is disabled,
    or as a best-effort match when it is enabled.
    """
    return f"{_TOPIC_ROOT}/{fmu_path}/rt/{type_name}_/TypeHashNotSupported"


# ---------------------------------------------------------------------------
# Message decoders
# (Field order and CDR alignment derived from msg/versioned/*.msg)
# ---------------------------------------------------------------------------

def decode_sensor_combined(raw: bytes) -> Dict[str, Any]:
    """
    SensorCombined — CDR layout (48 bytes):
      uint64 timestamp, float32[3] gyro_rad, uint32 gyro_integral_dt,
      int32 accel_timestamp_relative, float32[3] accelerometer_m_s2,
      uint32 accelerometer_integral_dt, uint8×4 (clipping + cal counts)
    """
    d = CDRDecoder(raw)
    return {
        "timestamp_us":     d.uint64(),
        "gyro_rad":         d.float32_array(3),
        "gyro_dt_us":       d.uint32(),
        "accel_ts_rel":     d.int32(),
        "accel_m_s2":       d.float32_array(3),
        "accel_dt_us":      d.uint32(),
        "accel_clipping":   d.uint8(),
        "gyro_clipping":    d.uint8(),
        "accel_cal_count":  d.uint8(),
        "gyro_cal_count":   d.uint8(),
    }


def decode_vehicle_attitude(raw: bytes) -> Dict[str, Any]:
    """
    VehicleAttitude — CDR layout (49 bytes):
      uint64 timestamp, uint64 timestamp_sample,
      float32[4] q (w,x,y,z Hamilton), float32[4] delta_q_reset,
      uint8 quat_reset_counter
    """
    d = CDRDecoder(raw)
    ts  = d.uint64()
    tss = d.uint64()
    q   = d.float32_array(4)   # [w, x, y, z]
    dq  = d.float32_array(4)
    rc  = d.uint8()

    # Derive Euler angles (ZYX, NED frame)
    w, x, y, z = q
    roll  = math.atan2(2*(w*x + y*z), 1 - 2*(x*x + y*y))
    pitch = math.asin(max(-1.0, min(1.0, 2*(w*y - z*x))))
    yaw   = math.atan2(2*(w*z + x*y), 1 - 2*(y*y + z*z))

    return {
        "timestamp_us":     ts,
        "timestamp_sample": tss,
        "q":                q,
        "delta_q_reset":    dq,
        "quat_reset_counter": rc,
        # derived
        "roll_deg":  math.degrees(roll),
        "pitch_deg": math.degrees(pitch),
        "yaw_deg":   math.degrees(yaw),
    }


def decode_vehicle_local_position(raw: bytes) -> Dict[str, Any]:
    """
    VehicleLocalPosition — decodes through vz field.
    Layout tracing (padding inserted by CDR alignment):
      [0]  uint64 timestamp
      [8]  uint64 timestamp_sample
      [16] bool×4 (xy_valid, z_valid, v_xy_valid, v_z_valid)
      [20] float32 x, y, z
      [32] float32[2] delta_xy
      [40] uint8 xy_reset_counter
      [44] float32 delta_z      ← 3 pad bytes at [41..43]
      [48] uint8 z_reset_counter
      [52] float32 vx           ← 3 pad bytes at [49..51]
      [56] float32 vy
      [60] float32 vz
    """
    d = CDRDecoder(raw)
    ts      = d.uint64()
    tss     = d.uint64()
    xy_ok   = d.bool_()
    z_ok    = d.bool_()
    vxy_ok  = d.bool_()
    vz_ok   = d.bool_()
    x       = d.float32()
    y       = d.float32()
    z       = d.float32()
    d.float32_array(2)      # delta_xy (skip)
    d.uint8()               # xy_reset_counter
    d.float32()             # delta_z  (CDR aligns to 4, consuming 3 pad bytes)
    d.uint8()               # z_reset_counter
    vx      = d.float32()   # CDR aligns to 4, consuming 3 pad bytes
    vy      = d.float32()
    vz      = d.float32()
    return {
        "timestamp_us":  ts,
        "xy_valid":      xy_ok,
        "z_valid":       z_ok,
        "v_xy_valid":    vxy_ok,
        "v_z_valid":     vz_ok,
        "x_m":           x,
        "y_m":           y,
        "z_m":           z,
        "vx_m_s":        vx,
        "vy_m_s":        vy,
        "vz_m_s":        vz,
        "alt_m":         -z,    # z is down in NED; positive alt = negative z
    }


_NAV_STATE_NAMES = {
    0:  "MANUAL",       1:  "ALTCTL",      2:  "POSCTL",
    3:  "MISSION",      4:  "LOITER",      5:  "RTL",
    10: "ACRO",         12: "DESCEND",     13: "TERMINATION",
    14: "OFFBOARD",     15: "STABILIZED",  17: "TAKEOFF",
    18: "LAND",         19: "FOLLOW_TGT",  21: "ORBIT",
}
_ARMING_STATE_NAMES = {1: "DISARMED", 2: "ARMED"}


def decode_vehicle_status(raw: bytes) -> Dict[str, Any]:
    """
    VehicleStatus — CDR layout through nav_state:
      [0]  uint64 timestamp
      [8]  uint64 armed_time
      [16] uint64 takeoff_time
      [24] uint8 arming_state
      [25] uint8 latest_arming_reason
      [26] uint8 latest_disarming_reason
           → pad to 32 for next uint64
      [32] uint64 nav_state_timestamp
      [40] uint8 nav_state_user_intention
      [41] uint8 nav_state
    """
    d = CDRDecoder(raw)
    ts         = d.uint64()
    armed_time = d.uint64()
    tkoff_time = d.uint64()
    arm_state  = d.uint8()
    d.uint8()                   # latest_arming_reason
    d.uint8()                   # latest_disarming_reason
    d.uint64()                  # nav_state_timestamp (CDR aligns, consuming pad)
    d.uint8()                   # nav_state_user_intention
    nav_state  = d.uint8()
    return {
        "timestamp_us":    ts,
        "armed_time_us":   armed_time,
        "arming_state":    arm_state,
        "arming_label":    _ARMING_STATE_NAMES.get(arm_state, f"UNK({arm_state})"),
        "nav_state":       nav_state,
        "nav_state_label": _NAV_STATE_NAMES.get(nav_state, f"UNK({nav_state})"),
    }


def decode_battery_status(raw: bytes) -> Dict[str, Any]:
    """
    BatteryStatus — CDR layout through cell_count:
      [0]  uint64 timestamp
      [8]  bool connected        ← 1 byte
           → pad to 12 for float32
      [12] float32 voltage_v
      [16] float32 current_a
      [20] float32 current_average_a
      [24] float32 discharged_mah
      [28] float32 remaining
      [32] float32 scale
      [36] float32 time_remaining_s
      [40] float32 temperature
      [44] uint8 cell_count
    """
    d = CDRDecoder(raw)
    ts          = d.uint64()
    connected   = d.bool_()
    voltage     = d.float32()   # CDR aligns, consuming 3 pad bytes
    current     = d.float32()
    d.float32()                  # current_average_a
    d.float32()                  # discharged_mah
    remaining   = d.float32()
    d.float32()                  # scale
    time_rem    = d.float32()
    temperature = d.float32()
    cell_count  = d.uint8()
    return {
        "timestamp_us":   ts,
        "connected":      connected,
        "voltage_v":      voltage,
        "current_a":      current,
        "remaining_pct":  remaining * 100.0,
        "time_rem_s":     time_rem,
        "temperature_c":  temperature,
        "cell_count":     cell_count,
    }


# ---------------------------------------------------------------------------
# Message encoders (for offboard control publisher test)
# ---------------------------------------------------------------------------

def encode_offboard_control_mode(ts_us: int, *, position: bool = False,
                                  velocity: bool = False) -> bytes:
    """
    OffboardControlMode — CDR layout (15 bytes):
      uint64 timestamp, bool×7 (position, velocity, acceleration,
      attitude, body_rate, thrust_and_torque, direct_actuator)
    """
    return (
        CDREncoder()
        .uint64(ts_us)
        .bool_(position)
        .bool_(velocity)
        .bool_(False)   # acceleration
        .bool_(False)   # attitude
        .bool_(False)   # body_rate
        .bool_(False)   # thrust_and_torque
        .bool_(False)   # direct_actuator
        .build()
    )


def encode_trajectory_setpoint(ts_us: int,
                                position: list[float] | None = None,
                                velocity: list[float] | None = None,
                                yaw: float = float("nan")) -> bytes:
    """
    TrajectorySetpoint — CDR layout (64 bytes):
      uint64 timestamp,
      float32[3] position, float32[3] velocity,
      float32[3] acceleration, float32[3] jerk,
      float32 yaw, float32 yawspeed
    NaN means "do not control this axis".
    """
    _nan = float("nan")
    pos = list(position) if position else [_nan, _nan, _nan]
    vel = list(velocity) if velocity else [_nan, _nan, _nan]
    return (
        CDREncoder()
        .uint64(ts_us)
        .float32_array(pos)
        .float32_array(vel)
        .float32_array([_nan, _nan, _nan])   # acceleration
        .float32_array([_nan, _nan, _nan])   # jerk
        .float32(yaw)
        .float32(_nan)                        # yawspeed
        .build()
    )


# ---------------------------------------------------------------------------
# Terminal helpers
# ---------------------------------------------------------------------------

_RESET  = "\033[0m"
_BOLD   = "\033[1m"
_RED    = "\033[31m"
_GREEN  = "\033[32m"
_YELLOW = "\033[33m"
_CYAN   = "\033[36m"
_WHITE  = "\033[37m"
_CLEAR  = "\033[2J\033[H"


def _col(text: str, color: str) -> str:
    return f"{color}{text}{_RESET}"


def _fmt_f(v: float, decimals: int = 3, width: int = 8) -> str:
    if math.isnan(v):
        return f"{'nan':>{width}}"
    return f"{v:{width}.{decimals}f}"


def _fmt_bool(v: bool) -> str:
    return _col("YES", _GREEN) if v else _col("NO ", _RED)


# ---------------------------------------------------------------------------
# State store (written by subscriber callbacks, read by display loop)
# ---------------------------------------------------------------------------

class State:
    def __init__(self):
        self._lock = threading.Lock()
        self.attitude:   Optional[Dict] = None
        self.imu:        Optional[Dict] = None
        self.local_pos:  Optional[Dict] = None
        self.status:     Optional[Dict] = None
        self.battery:    Optional[Dict] = None
        self.msg_counts: Dict[str, int] = {
            "attitude": 0, "imu": 0, "local_pos": 0, "status": 0, "battery": 0
        }
        self.last_update: float = 0.0

    def update(self, key: str, val: Dict) -> None:
        with self._lock:
            setattr(self, key, val)
            self.msg_counts[key] += 1
            self.last_update = time.monotonic()

    def snapshot(self):
        with self._lock:
            return (
                self.attitude, self.imu, self.local_pos,
                self.status, self.battery,
                dict(self.msg_counts), self.last_update,
            )


# ---------------------------------------------------------------------------
# Monitor display
# ---------------------------------------------------------------------------

def _render_dashboard(att, imu, lpos, stat, batt, counts, last_update):
    now = time.monotonic()
    age = now - last_update if last_update else 999.0

    lines = [
        _CLEAR,
        _col("╔══════════════════════════════════════════════════════╗", _CYAN),
        _col("║        PX4 Nucleo-H753ZI  ·  Zenoh Monitor           ║", _CYAN),
        _col("╚══════════════════════════════════════════════════════╝", _CYAN),
        f"  Last message: {age:.1f}s ago   "
        + f"msgs: att={counts['attitude']} imu={counts['imu']} "
        + f"pos={counts['local_pos']} stat={counts['status']} batt={counts['battery']}",
        "",
    ]

    # --- Vehicle Status ---
    lines.append(_col("  ── Vehicle Status ─────────────────────────────────", _YELLOW))
    if stat:
        arm_color = _GREEN if stat["arming_state"] == 2 else _RED
        lines.append(f"  Arming   : {_col(stat['arming_label'], arm_color)}")
        lines.append(f"  Nav mode : {_col(stat['nav_state_label'], _CYAN)}")
    else:
        lines.append("  (no data)")
    lines.append("")

    # --- Attitude ---
    lines.append(_col("  ── Attitude (roll / pitch / yaw) ───────────────────", _YELLOW))
    if att:
        r, p, y = att["roll_deg"], att["pitch_deg"], att["yaw_deg"]
        lines.append(f"  Roll  : {_fmt_f(r, 2, 7)} °")
        lines.append(f"  Pitch : {_fmt_f(p, 2, 7)} °")
        lines.append(f"  Yaw   : {_fmt_f(y, 2, 7)} °")
        lines.append(f"  q     : [{' '.join(_fmt_f(v, 4, 7) for v in att['q'])}]")
    else:
        lines.append("  (no data)")
    lines.append("")

    # --- Local Position ---
    lines.append(_col("  ── Local Position (NED) ────────────────────────────", _YELLOW))
    if lpos:
        xy_s  = _fmt_bool(lpos["xy_valid"])
        z_s   = _fmt_bool(lpos["z_valid"])
        vxy_s = _fmt_bool(lpos["v_xy_valid"])
        vz_s  = _fmt_bool(lpos["v_z_valid"])
        lines.append(f"  xy_valid={xy_s}  z_valid={z_s}  "
                     f"v_xy_valid={vxy_s}  v_z_valid={vz_s}")
        lines.append(f"  x={_fmt_f(lpos['x_m'])} m   "
                     f"y={_fmt_f(lpos['y_m'])} m   "
                     f"alt={_fmt_f(lpos['alt_m'])} m")
        lines.append(f"  vx={_fmt_f(lpos['vx_m_s'])} m/s   "
                     f"vy={_fmt_f(lpos['vy_m_s'])} m/s   "
                     f"vz={_fmt_f(lpos['vz_m_s'])} m/s")
    else:
        lines.append("  (no data)")
    lines.append("")

    # --- IMU ---
    lines.append(_col("  ── IMU (sensor_combined) ───────────────────────────", _YELLOW))
    if imu:
        gx, gy, gz = imu["gyro_rad"]
        ax, ay, az = imu["accel_m_s2"]
        lines.append(f"  gyro  : {_fmt_f(gx)} {_fmt_f(gy)} {_fmt_f(gz)}  rad/s")
        lines.append(f"  accel : {_fmt_f(ax)} {_fmt_f(ay)} {_fmt_f(az)}  m/s²")
    else:
        lines.append("  (no data)")
    lines.append("")

    # --- Battery ---
    lines.append(_col("  ── Battery ─────────────────────────────────────────", _YELLOW))
    if batt and batt["connected"]:
        pct = batt["remaining_pct"]
        pct_color = _GREEN if pct > 30 else (_YELLOW if pct > 15 else _RED)
        lines.append(f"  Voltage  : {_fmt_f(batt['voltage_v'], 2, 6)} V")
        lines.append(f"  Current  : {_fmt_f(batt['current_a'], 2, 6)} A")
        lines.append(f"  Remaining: {_col(f'{pct:.1f} %', pct_color)}")
        if not math.isnan(batt["time_rem_s"]):
            lines.append(f"  Time rem : {batt['time_rem_s']:.0f} s")
        if not math.isnan(batt["temperature_c"]):
            lines.append(f"  Temp     : {batt['temperature_c']:.1f} °C")
    else:
        lines.append("  (not connected)")
    lines.append("")
    lines.append(_col("  Press Ctrl+C to quit.", _WHITE))

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Subcommand: monitor
# ---------------------------------------------------------------------------

def cmd_monitor(args):
    state = State()

    def _make_callback(decoder_fn, state_key):
        def cb(sample):
            try:
                state.update(state_key, decoder_fn(bytes(sample.payload.to_bytes())))
            except Exception as e:
                pass  # tolerate partial/malformed messages during bring-up
        return cb

    cfg = zenoh.Config()
    if args.router:
        cfg.insert_json5("connect/endpoints", f'["{args.router}"]')
    elif args.peer:
        cfg.insert_json5("scouting/multicast/address", f'"{args.peer}"')

    with zenoh.open(cfg) as session:
        subs = [
            session.declare_subscriber(
                sub_keyexpr("out/vehicle_attitude"),
                _make_callback(decode_vehicle_attitude, "attitude")),
            session.declare_subscriber(
                sub_keyexpr("out/sensor_combined"),
                _make_callback(decode_sensor_combined, "imu")),
            session.declare_subscriber(
                sub_keyexpr("out/vehicle_local_position"),
                _make_callback(decode_vehicle_local_position, "local_pos")),
            session.declare_subscriber(
                sub_keyexpr("out/vehicle_status"),
                _make_callback(decode_vehicle_status, "status")),
            session.declare_subscriber(
                sub_keyexpr("out/battery_status"),
                _make_callback(decode_battery_status, "battery")),
        ]

        print("Connected. Waiting for data…  (Ctrl+C to quit)")
        try:
            while True:
                att, imu, lpos, stat, batt, counts, last = state.snapshot()
                print(_render_dashboard(att, imu, lpos, stat, batt, counts, last),
                      end="", flush=True)
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            for s in subs:
                s.undeclare()


# ---------------------------------------------------------------------------
# Subcommand: echo
# ---------------------------------------------------------------------------

_ECHO_DECODERS = {
    "vehicle_attitude":       ("out/vehicle_attitude",       decode_vehicle_attitude),
    "sensor_combined":        ("out/sensor_combined",        decode_sensor_combined),
    "vehicle_local_position": ("out/vehicle_local_position", decode_vehicle_local_position),
    "vehicle_status":         ("out/vehicle_status",         decode_vehicle_status),
    "battery_status":         ("out/battery_status",         decode_battery_status),
}


def cmd_echo(args):
    if args.topic not in _ECHO_DECODERS:
        print(f"Unknown topic '{args.topic}'.  Available: {', '.join(_ECHO_DECODERS)}")
        sys.exit(1)

    fmu_path, decoder = _ECHO_DECODERS[args.topic]
    count = [0]

    def cb(sample):
        try:
            msg = decoder(bytes(sample.payload.to_bytes()))
            count[0] += 1
            ts = msg.get("timestamp_us", 0)
            print(f"\n[{count[0]}] ts={ts} us  key={sample.key_expr}")
            for k, v in msg.items():
                if k == "timestamp_us":
                    continue
                if isinstance(v, list):
                    vals = "  ".join(f"{x:.4f}" for x in v)
                    print(f"  {k:30s}: [{vals}]")
                elif isinstance(v, float):
                    print(f"  {k:30s}: {v:.6f}")
                else:
                    print(f"  {k:30s}: {v}")
        except Exception as e:
            print(f"  decode error: {e} (raw {len(bytes(sample.payload.to_bytes()))} bytes)")

    cfg = zenoh.Config()
    if args.router:
        cfg.insert_json5("connect/endpoints", f'["{args.router}"]')

    with zenoh.open(cfg) as session:
        sub = session.declare_subscriber(sub_keyexpr(fmu_path), cb)
        print(f"Subscribed to '{sub_keyexpr(fmu_path)}'.  Ctrl+C to quit.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            sub.undeclare()


# ---------------------------------------------------------------------------
# Subcommand: offboard
# ---------------------------------------------------------------------------

def cmd_offboard(args):
    """
    Sends offboard_control_mode + trajectory_setpoint at 20 Hz.
    The vehicle must be armed and OFFBOARD mode engaged externally
    (e.g. via RC switch or QGroundControl) before this takes effect.
    """
    fmu_in_ocm = pub_keyexpr("in/offboard_control_mode", "OffboardControlMode")
    fmu_in_tsp = pub_keyexpr("in/trajectory_setpoint",   "TrajectorySetpoint")

    pos_mode = (args.pos is not None)
    vel_mode = (args.vel is not None)

    if not pos_mode and not vel_mode:
        print("Specify --pos or --vel (or both).")
        sys.exit(1)

    pos = [float(x) for x in args.pos] if pos_mode else None
    vel = [float(x) for x in args.vel] if vel_mode else None
    yaw = float(args.yaw) if args.yaw is not None else float("nan")

    cfg = zenoh.Config()
    if args.router:
        cfg.insert_json5("connect/endpoints", f'["{args.router}"]')

    print(f"Publishing offboard setpoints at 20 Hz (Ctrl+C to stop).")
    print(f"  position : {pos}")
    print(f"  velocity : {vel}")
    print(f"  yaw (rad): {yaw:.3f}" if not math.isnan(yaw) else "  yaw (rad): NaN (uncontrolled)")
    print()

    with zenoh.open(cfg) as session:
        pub_ocm = session.declare_publisher(fmu_in_ocm)
        pub_tsp = session.declare_publisher(fmu_in_tsp)
        try:
            i = 0
            while True:
                ts = int(time.monotonic() * 1e6) & 0xFFFFFFFFFFFFFFFF
                pub_ocm.put(encode_offboard_control_mode(
                    ts, position=pos_mode, velocity=vel_mode))
                pub_tsp.put(encode_trajectory_setpoint(ts, pos, vel, yaw))
                i += 1
                if i % 20 == 0:
                    print(f"\r  {i} messages sent…", end="", flush=True)
                time.sleep(0.05)  # 20 Hz
        except KeyboardInterrupt:
            print("\nStopped.")
        finally:
            pub_ocm.undeclare()
            pub_tsp.undeclare()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _add_transport_args(p):
    grp = p.add_mutually_exclusive_group()
    grp.add_argument(
        "--router", metavar="LOCATOR",
        help="Zenoh router locator, e.g. tcp/192.168.0.1:7447")
    grp.add_argument(
        "--peer", metavar="MCAST",
        help="Multicast peer locator, e.g. udp/224.0.0.224:7446")


def main():
    ap = argparse.ArgumentParser(
        description="PX4 Zenoh host-side test tool (Nucleo-H753ZI)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__)

    sub = ap.add_subparsers(dest="cmd", required=True)

    # monitor
    p_mon = sub.add_parser("monitor", help="Live terminal dashboard of all key topics")
    _add_transport_args(p_mon)

    # echo
    p_echo = sub.add_parser("echo", help="Print decoded messages from one topic")
    p_echo.add_argument("topic", choices=list(_ECHO_DECODERS),
                        help="Topic to subscribe to")
    _add_transport_args(p_echo)

    # offboard
    p_off = sub.add_parser("offboard",
                            help="Publish trajectory_setpoint + offboard_control_mode")
    p_off.add_argument("--pos", nargs=3, metavar=("X", "Y", "Z"),
                       help="NED position setpoint in metres")
    p_off.add_argument("--vel", nargs=3, metavar=("VX", "VY", "VZ"),
                       help="NED velocity setpoint in m/s")
    p_off.add_argument("--yaw", metavar="RAD",
                       help="Yaw setpoint in radians (-π..+π)")
    _add_transport_args(p_off)

    args = ap.parse_args()

    dispatch = {"monitor": cmd_monitor, "echo": cmd_echo, "offboard": cmd_offboard}
    dispatch[args.cmd](args)


if __name__ == "__main__":
    main()
