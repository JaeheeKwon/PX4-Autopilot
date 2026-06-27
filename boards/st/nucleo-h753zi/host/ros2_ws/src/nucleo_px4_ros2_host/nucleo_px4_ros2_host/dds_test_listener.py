#!/usr/bin/env python3
"""Minimal ROS 2 listener that exits PASS/FAIL for a DDS smoke test."""

import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class DdsTestListener(Node):
    def __init__(self) -> None:
        super().__init__("nucleo_dds_test_listener")
        self.declare_parameter("topic", "/nucleo/dds_quick_test")
        self.declare_parameter("expected", "nucleo-dds-ok")
        self.declare_parameter("timeout_sec", 10.0)

        topic = str(self.get_parameter("topic").value)
        self.expected = str(self.get_parameter("expected").value)
        self.timeout_sec = max(float(self.get_parameter("timeout_sec").value), 0.1)
        self.received = False
        self.create_subscription(String, topic, self._on_message, 10)
        self.get_logger().info(
            f"Waiting up to {self.timeout_sec:.1f}s for '{self.expected}' on {topic}"
        )

    def _on_message(self, msg: String) -> None:
        if self.expected in msg.data:
            self.received = True
            self.get_logger().info(f"PASS: received '{msg.data}'")
        else:
            self.get_logger().warning(f"Ignoring unexpected message '{msg.data}'")


def main(args=None) -> None:
    rclpy.init(args=args)
    node = DdsTestListener()
    deadline = time.monotonic() + node.timeout_sec
    try:
        while rclpy.ok() and not node.received and time.monotonic() < deadline:
            rclpy.spin_once(node, timeout_sec=0.1)
        passed = node.received
        if not passed:
            node.get_logger().error("FAIL: no matching DDS message before timeout")
    except KeyboardInterrupt:
        passed = False
    finally:
        node.destroy_node()
        rclpy.shutdown()

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
