#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32


class BatteryNode(Node):
    """
    Симулятор батареи робота.
    Разряжается на 1% каждую секунду.
    """

    def __init__(self):
        super().__init__('battery_node')

        # Начальный заряд
        self.battery_level = 100.0

        # Последний залогированный порог
        self.last_logged_threshold = 100

        # Publisher для уровня батареи
        self.battery_publisher = self.create_publisher(
            Float32,
            '/battery_level',
            10
        )

        # Таймер 1 Hz (каждую секунду)
        self.timer = self.create_timer(1.0, self.update_battery)

        self.get_logger().info('Battery Node started - Initial charge: 100%')

    def update_battery(self):
        """
        Обновление уровня батареи каждую секунду.
        """
        # Если батарея уже разряжена — публикуем 0 и не разряжаем дальше
        if self.battery_level <= 0.0:
            self.battery_level = 0.0
            msg = Float32()
            msg.data = 0.0
            self.battery_publisher.publish(msg)
            return

        # Разряд -1.0% каждую секунду
        self.battery_level -= 1.0

        # Ограничиваем минимум 0%
        if self.battery_level < 0.0:
            self.battery_level = 0.0

        # Публикуем текущий уровень
        msg = Float32()
        msg.data = self.battery_level
        self.battery_publisher.publish(msg)

        # Логирование каждые 10% снижения
        current_threshold = int(self.battery_level // 10) * 10
        if current_threshold < self.last_logged_threshold:
            self.last_logged_threshold = current_threshold
            self.get_logger().info(f'Battery: {int(self.battery_level)}%')

        # Логирование при полной разрядке
        if self.battery_level <= 0.0:
            self.get_logger().warn('Battery: 0%')


def main(args=None):
    rclpy.init(args=args)
    node = BatteryNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()