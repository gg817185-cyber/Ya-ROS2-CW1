#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, String


class StatusDisplay(Node):
    """
    Узел статуса робота.
    Агрегирует данные батареи и датчика расстояния.
    Публикует текстовый статус системы.
    """

    def __init__(self):
        super().__init__('status_display')

        # Начальные параметры
        self.battery_level = 100.0     # последнее значение батареи (%)
        self.distance = 3.0            # последнее расстояние (метры)
        self.current_status = 'ALL OK' # текущий статус

        # Subscriber для уровня батареи
        self.battery_subscriber = self.create_subscription(
            Float32,
            '/battery_level',
            self.battery_callback,
            10
        )

        # Subscriber для расстояния
        self.distance_subscriber = self.create_subscription(
            Float32,
            '/distance',
            self.distance_callback,
            10
        )

        # Publisher для статуса робота
        self.status_publisher = self.create_publisher(
            String,
            '/robot_status',
            10
        )

        # Таймер 2 Hz (каждые 0.5 секунды)
        self.timer = self.create_timer(0.5, self.update_status)

        self.get_logger().info('Status Display started - Status: ALL OK')

    def battery_callback(self, msg):
        """
        Получаем уровень батареи.
        """
        self.battery_level = msg.data

    def distance_callback(self, msg):
        """
        Получаем расстояние до препятствия.
        """
        self.distance = msg.data

    def compute_status(self):
        # CRITICAL — самый высокий приоритет
        if self.battery_level < 10.0 or self.distance < 0.7:
            return 'CRITICAL'

        # WARNING по батарее
        if self.battery_level < 20.0:
            return 'WARNING: Low battery'

        # WARNING по расстоянию
        if self.distance < 1.0:
            return 'WARNING: Obstacle close'

        # Всё в норме
        return 'ALL OK'

    def update_status(self):
        """
        Обновление и публикация статуса каждые 0.5 секунды.
        """
        new_status = self.compute_status()

        # Логируем только при изменении статуса
        if new_status != self.current_status:
            self.get_logger().info(
                f'Status changed: {self.current_status} -> {new_status} '
                f'(battery={self.battery_level:.1f}%, distance={self.distance:.2f}m)'
            )
            self.current_status = new_status

        # Публикуем текущий статус
        msg = String()
        msg.data = self.current_status
        self.status_publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = StatusDisplay()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()