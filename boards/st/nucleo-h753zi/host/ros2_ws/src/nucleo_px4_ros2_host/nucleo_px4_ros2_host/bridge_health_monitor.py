#!/usr/bin/env python3
"""Exercise the PX4 DDS bridge without publishing flight commands."""

import math
import time
from typing import Dict, Optional

import rclpy
from px4_msgs.msg import (
    OnboardComputerStatus,
    SensorCombined,
    TimesyncStatus,
    VehicleOdometry,
    VehicleStatus,
)
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy


class BridgeHealthMonitor(Node):
    """Monitor PX4 outputs and publish a non-commanding companion heartbeat."""

    def __init__(self) -> None:
        super().__init__("nucleo_px4_bridge_health")
        self.declare_parameter("px4_namespace", "")
        self.declare_parameter(
            "vehicle_status_topic", "/fmu/out/vehicle_status_v4"
        )

        self._namespace = self._normalize_namespace(
            str(self.get_parameter("px4_namespace").value)
        )
        status_topic = str(self.get_parameter("vehicle_status_topic").value)

        output_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            history=HistoryPolicy.KEEP_LAST,
            depth=5,
        )
        input_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )

        self._start_time = time.monotonic()
        self._last_report_time = self._start_time
        self._counts: Dict[str, int] = {
            "vehicle_status": 0,
            "vehicle_odometry": 0,
            "sensor_combined": 0,
            "timesync_status": 0,
        }
        self._last_counts = dict(self._counts)
        self._last_rx: Dict[str, Optional[float]] = {
            name: None for name in self._counts
        }
        self._status: Optional[VehicleStatus] = None
        self._odometry: Optional[VehicleOdometry] = None
        self._timesync: Optional[TimesyncStatus] = None

        self.create_subscription(
            VehicleStatus,
            self._topic(status_topic),
            self._on_vehicle_status,
            output_qos,
        )
        self.create_subscription(
            VehicleOdometry,
            self._topic("/fmu/out/vehicle_odometry"),
            self._on_vehicle_odometry,
            output_qos,
        )
        self.create_subscription(
            SensorCombined,
            self._topic("/fmu/out/sensor_combined"),
            lambda _msg: self._record("sensor_combined"),
            output_qos,
        )
        self.create_subscription(
            TimesyncStatus,
            self._topic("/fmu/out/timesync_status"),
            self._on_timesync_status,
            output_qos,
        )
        self._onboard_status_publisher = self.create_publisher(
            OnboardComputerStatus,
            self._topic("/fmu/in/onboard_computer_status"),
            input_qos,
        )

        self.create_timer(1.0, self._publish_onboard_status)
        self.create_timer(2.0, self._report)
        self.get_logger().info(
            "Monitoring PX4 DDS bridge; no flight commands will be published."
        )

    @staticmethod
    def _normalize_namespace(namespace: str) -> str:
        namespace = namespace.strip().strip("/")
        return f"/{namespace}" if namespace else ""

    def _topic(self, topic: str) -> str:
        topic = "/" + topic.strip("/")
        return f"{self._namespace}{topic}"

    def _record(self, name: str) -> None:
        self._counts[name] += 1
        self._last_rx[name] = time.monotonic()

    def _on_vehicle_status(self, msg: VehicleStatus) -> None:
        self._record("vehicle_status")
        self._status = msg

    def _on_vehicle_odometry(self, msg: VehicleOdometry) -> None:
        self._record("vehicle_odometry")
        self._odometry = msg

    def _on_timesync_status(self, msg: TimesyncStatus) -> None:
        self._record("timesync_status")
        self._timesync = msg

    def _publish_onboard_status(self) -> None:
        msg = OnboardComputerStatus()
        msg.timestamp = self.get_clock().now().nanoseconds // 1000
        msg.uptime = int((time.monotonic() - self._start_time) * 1000)
        msg.type = 0
        msg.cpu_cores = [0] * 8
        msg.cpu_combined = [0] * 10
        msg.gpu_cores = [0] * 4
        msg.gpu_combined = [0] * 10
        # INT8_MAX is PX4's explicit "temperature unavailable" sentinel.
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
        self._onboard_status_publisher.publish(msg)

    def _report(self) -> None:
        now = time.monotonic()
        period = max(now - self._last_report_time, 1e-6)
        rates = {
            name: (count - self._last_counts[name]) / period
            for name, count in self._counts.items()
        }
        stale = [
            name
            for name, last_rx in self._last_rx.items()
            if last_rx is None or now - last_rx > 5.0
        ]
        self._last_counts = dict(self._counts)
        self._last_report_time = now

        details = []
        if self._status is not None:
            armed_state = getattr(VehicleStatus, "ARMING_STATE_ARMED", 2)
            details.append(
                f"nav={self._status.nav_state} "
                f"armed={self._status.arming_state == armed_state}"
            )
        if self._odometry is not None:
            position = self._odometry.position
            details.append(
                "ned=(" + ",".join(self._format(value) for value in position) + ")"
            )
        if self._timesync is not None:
            details.append(f"rtt_us={self._timesync.round_trip_time}")

        rates_text = " ".join(
            f"{name}={rate:.1f}Hz" for name, rate in rates.items()
        )
        stale_text = ",".join(stale) if stale else "none"
        self.get_logger().info(
            f"rx {rates_text} stale={stale_text} {' '.join(details)}"
        )

    @staticmethod
    def _format(value: float) -> str:
        return "nan" if math.isnan(value) else f"{value:.2f}"


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
