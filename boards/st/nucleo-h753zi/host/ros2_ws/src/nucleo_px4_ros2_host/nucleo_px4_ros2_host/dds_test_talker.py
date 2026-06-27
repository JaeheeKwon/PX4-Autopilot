#!/usr/bin/env python3
"""Minimal ROS 2 talker for checking DDS discovery and delivery."""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class DdsTestTalker(Node):
    def __init__(self) -> None:
        super().__init__("nucleo_dds_test_talker")
        self.declare_parameter("topic", "/nucleo/dds_quick_test")
        self.declare_parameter("message", "nucleo-dds-ok")
        self.declare_parameter("rate_hz", 2.0)

        topic = str(self.get_parameter("topic").value)
        self._text = str(self.get_parameter("message").value)
        rate_hz = max(float(self.get_parameter("rate_hz").value), 0.1)
        self._sequence = 0
        self._publisher = self.create_publisher(String, topic, 10)
        self.create_timer(1.0 / rate_hz, self._publish)
        self.get_logger().info(f"Publishing DDS test messages on {topic}")

    def _publish(self) -> None:
        msg = String()
        msg.data = f"{self._text} sequence={self._sequence}"
        self._publisher.publish(msg)
        self.get_logger().info(msg.data)
        self._sequence += 1


def main(args=None) -> None:
    rclpy.init(args=args)
    node = DdsTestTalker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
