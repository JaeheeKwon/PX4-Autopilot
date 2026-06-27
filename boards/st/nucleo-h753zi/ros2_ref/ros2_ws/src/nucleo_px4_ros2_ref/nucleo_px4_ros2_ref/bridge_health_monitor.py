#!/usr/bin/env python3
"""Monitor the PX4 uXRCE-DDS bridge without commanding flight."""

import math
import time
from typing import Dict

import rclpy
from rclpy.node import Node
from rclpy.qos import (
    DurabilityPolicy,
    HistoryPolicy,
    QoSProfile,
    ReliabilityPolicy,
)

from px4_msgs.msg import (
    OnboardComputerStatus,
    SensorCombined,
    TimesyncStatus,
    VehicleOdometry,
    VehicleStatus,
)


class BridgeHealthMonitor(Node):
    """Subscribe to PX4 telemetry and publish a harmless companion heartbeat."""

    def __init__(self) -> None:
        super().__init__("nucleo_bridge_health_monitor")

        self.declare_parameter("px4_namespace", "")
        namespace = self.get_parameter("px4_namespace").value
        self._prefix = self._normalize_namespace(str(namespace))

        # PX4 publishes DDS topics as best-effort and transient-local.
        self._px4_output_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=5,
        )

        # PX4 subscribers are best-effort and volatile.
        self._px4_input_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )

        self._start_monotonic = time.monotonic()
        self._last_report_monotonic = self._start_monotonic
        self._counts: Dict[str, int] = {
            "vehicle_status": 0,
            "vehicle_odometry": 0,
            "sensor_combined": 0,
            "timesync_status": 0,
        }
        self._last_report_counts = dict(self._counts)
        self._last_status = None
        self._last_odometry = None
        self._last_timesync = None

        self.create_subscription(
            VehicleStatus,
            self._topic("/fmu/out/vehicle_status_v4"),
            self._vehicle_status_callback,
            self._px4_output_qos,
        )
        self.create_subscription(
            VehicleOdometry,
            self._topic("/fmu/out/vehicle_odometry"),
            self._vehicle_odometry_callback,
            self._px4_output_qos,
        )
        self.create_subscription(
            SensorCombined,
            self._topic("/fmu/out/sensor_combined"),
            self._sensor_combined_callback,
            self._px4_output_qos,
        )
        self.create_subscription(
            TimesyncStatus,
            self._topic("/fmu/out/timesync_status"),
            self._timesync_status_callback,
            self._px4_output_qos,
        )

        self._onboard_status_pub = self.create_publisher(
            OnboardComputerStatus,
            self._topic("/fmu/in/onboard_computer_status"),
            self._px4_input_qos,
        )

        self.create_timer(1.0, self._publish_onboard_status)
        self.create_timer(2.0, self._report_health)

        self.get_logger().info(
            "Monitoring PX4 DDS topics under namespace "
            f"'{self._prefix or '/'}'. Publishing onboard_computer_status at 1 Hz."
        )

    @staticmethod
    def _normalize_namespace(namespace: str) -> str:
        namespace = namespace.strip()
        if not namespace:
            return ""
        if not namespace.startswith("/"):
            namespace = "/" + namespace
        return namespace.rstrip("/")

    def _topic(self, relative_topic: str) -> str:
        return f"{self._prefix}{relative_topic}"

    def _now_us(self) -> int:
        return int(self.get_clock().now().nanoseconds / 1000)

    def _vehicle_status_callback(self, msg: VehicleStatus) -> None:
        self._counts["vehicle_status"] += 1
        self._last_status = msg

    def _vehicle_odometry_callback(self, msg: VehicleOdometry) -> None:
        self._counts["vehicle_odometry"] += 1
        self._last_odometry = msg

    def _sensor_combined_callback(self, _msg: SensorCombined) -> None:
        self._counts["sensor_combined"] += 1

    def _timesync_status_callback(self, msg: TimesyncStatus) -> None:
        self._counts["timesync_status"] += 1
        self._last_timesync = msg

    def _publish_onboard_status(self) -> None:
        msg = OnboardComputerStatus()
        msg.timestamp = self._now_us()
        msg.uptime = int((time.monotonic() - self._start_monotonic) * 1000)
        msg.type = 0
        msg.cpu_cores = [0] * 8
        msg.cpu_combined = [0] * 10
        msg.gpu_cores = [0] * 4
        msg.gpu_combined = [0] * 10
        msg.temperature_board = 127
        msg.temperature_core = [127] * 8
        msg.fan_speed = [0] * 4
        msg.ram_usage = 0
        msg.ram_total = 0
        msg.storage_type = [0] * 4
        msg.storage_usage = [0] * 4
        msg.storage_total = [0] * 4
        msg.link_type = [0] * 6
        msg.link_tx_rate = [0] * 6
        msg.link_rx_rate = [0] * 6
        msg.link_tx_max = [0] * 6
        msg.link_rx_max = [0] * 6
        self._onboard_status_pub.publish(msg)

    def _report_health(self) -> None:
        now = time.monotonic()
        dt = max(now - self._last_report_monotonic, 1e-6)
        rates = {
            name: (self._counts[name] - self._last_report_counts[name]) / dt
            for name in self._counts
        }
        self._last_report_counts = dict(self._counts)
        self._last_report_monotonic = now

        status_text = "status=not_received"
        if self._last_status is not None:
            armed_value = getattr(VehicleStatus, "ARMING_STATE_ARMED", 2)
            armed = "armed" if self._last_status.arming_state == armed_value else "disarmed"
            status_text = (
                f"nav_state={self._last_status.nav_state} "
                f"arming={armed} hil_state={self._last_status.hil_state}"
            )

        odom_text = "odom=not_received"
        if self._last_odometry is not None:
            pos = self._last_odometry.position
            vel = self._last_odometry.velocity
            odom_text = (
                "odom_pos_ned="
                f"({self._fmt(pos[0])}, {self._fmt(pos[1])}, {self._fmt(pos[2])}) "
                "vel_ned="
                f"({self._fmt(vel[0])}, {self._fmt(vel[1])}, {self._fmt(vel[2])})"
            )

        timesync_text = "timesync=not_received"
        if self._last_timesync is not None:
            timesync_text = (
                f"timesync_rtt_us={self._last_timesync.round_trip_time} "
                f"offset_us={self._last_timesync.estimated_offset}"
            )

        self.get_logger().info(
            "rx_hz "
            f"vehicle_status={rates['vehicle_status']:.1f} "
            f"vehicle_odometry={rates['vehicle_odometry']:.1f} "
            f"sensor_combined={rates['sensor_combined']:.1f} "
            f"timesync_status={rates['timesync_status']:.1f} | "
            f"{status_text} | {odom_text} | {timesync_text}"
        )

    @staticmethod
    def _fmt(value: float) -> str:
        if math.isnan(value):
            return "nan"
        return f"{value:.2f}"


def main(args=None) -> None:
    rclpy.init(args=args)
    node = BridgeHealthMonitor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
