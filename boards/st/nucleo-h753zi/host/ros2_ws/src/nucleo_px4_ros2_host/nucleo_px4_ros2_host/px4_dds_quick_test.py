#!/usr/bin/env python3
"""Short, non-commanding, bidirectional PX4 uXRCE-DDS connection test."""

import time
from typing import Set

import rclpy
from px4_msgs.msg import OnboardComputerStatus, TimesyncStatus, VehicleStatus
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy


class Px4DdsQuickTest(Node):
    def __init__(self) -> None:
        super().__init__("nucleo_px4_dds_quick_test")
        self.declare_parameter("px4_namespace", "")
        self.declare_parameter("vehicle_status_topic", "/fmu/out/vehicle_status_v4")
        self.declare_parameter("timeout_sec", 15.0)

        namespace = str(self.get_parameter("px4_namespace").value).strip(" /")
        self._prefix = f"/{namespace}" if namespace else ""
        self.timeout_sec = max(float(self.get_parameter("timeout_sec").value), 1.0)
        status_topic = str(self.get_parameter("vehicle_status_topic").value)
        self.received: Set[str] = set()
        self._start = time.monotonic()

        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )
        self.create_subscription(
            VehicleStatus, self._topic(status_topic), self._on_status, qos
        )
        self.create_subscription(
            TimesyncStatus,
            self._topic("/fmu/out/timesync_status"),
            self._on_timesync,
            qos,
        )
        self._heartbeat = self.create_publisher(
            OnboardComputerStatus,
            self._topic("/fmu/in/onboard_computer_status"),
            qos,
        )
        self.create_timer(0.5, self._publish_heartbeat)
        self.get_logger().info(
            "Waiting for PX4 status and time sync; publishing no flight commands"
        )

    def _topic(self, topic: str) -> str:
        return f"{self._prefix}/{'/'.join(topic.strip('/').split('/'))}"

    def _on_status(self, msg: VehicleStatus) -> None:
        if "vehicle_status" not in self.received:
            self.get_logger().info(
                f"RX vehicle status: nav_state={msg.nav_state}, "
                f"arming_state={msg.arming_state}"
            )
        self.received.add("vehicle_status")

    def _on_timesync(self, msg: TimesyncStatus) -> None:
        if "timesync_status" not in self.received:
            self.get_logger().info(
                f"RX time sync: round_trip_time={msg.round_trip_time}us"
            )
        self.received.add("timesync_status")

    def _publish_heartbeat(self) -> None:
        msg = OnboardComputerStatus()
        msg.timestamp = self.get_clock().now().nanoseconds // 1000
        msg.uptime = int((time.monotonic() - self._start) * 1000)
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
        self._heartbeat.publish(msg)

    @property
    def passed(self) -> bool:
        outbound_ok = {"vehicle_status", "timesync_status"} <= self.received
        inbound_reader_ok = self._heartbeat.get_subscription_count() > 0
        return outbound_ok and inbound_reader_ok


def main(args=None) -> None:
    rclpy.init(args=args)
    node = Px4DdsQuickTest()
    deadline = time.monotonic() + node.timeout_sec
    try:
        while rclpy.ok() and not node.passed and time.monotonic() < deadline:
            rclpy.spin_once(node, timeout_sec=0.1)
        passed = node.passed
        if passed:
            node.get_logger().info(
                "PASS: PX4 DDS outbound topics received and inbound reader matched"
            )
        else:
            node.get_logger().error(
                "FAIL: received="
                f"{sorted(node.received)}, inbound_readers="
                f"{node._heartbeat.get_subscription_count()}"
            )
    except KeyboardInterrupt:
        passed = False
    finally:
        node.destroy_node()
        rclpy.shutdown()

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
