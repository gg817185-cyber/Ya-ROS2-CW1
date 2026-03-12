#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from geometry_msgs.msg import Twist


class DistanceSensor(Node):
    """
    Симулятор датчика расстояния.
    Расстояние меняется в зависимости от движения робота.
    """

    def __init__(self):
        super().__init__('distance_sensor')

        # Начальные параметры
        self.distance = 3.0       # начальное расстояние (метры)
        self.linear_x = 0.0       # последняя скорость по оси X

        # Publisher для расстояния
        self.distance_publisher = self.create_publisher(
            Float32,
            '/distance',
            10
        )

        # Subscriber для команд скорости
        self.cmd_vel_subscriber = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10
        )

        # Таймер 5 Hz (каждые 0.2 секунды)
        self.timer = self.create_timer(0.2, self.update_distance)

        self.get_logger().info('Distance Sensor started - Initial distance: 3.0m')

    def cmd_vel_callback(self, msg):
        """
        Получаем команду скорости от робота.
        """
        self.linear_x = msg.linear.x

    def update_distance(self):
        """
        Обновление расстояния каждые 0.2 секунды.
        """
        if self.linear_x > 0.0:
            # Движение вперёд — сближаемся с препятствием
            self.distance -= 0.2
            # Ограничиваем минимум 0.5 метра
            if self.distance < 0.5:
                self.distance = 0.5

        elif self.linear_x < 0.0:
            # Движение назад — удаляемся от препятствия
            self.distance += 0.2
            # Ограничиваем максимум 3.0 метра
            if self.distance > 3.0:
                self.distance = 3.0

        else:
            # Робот стоит — расстояние 3.0 метра
            self.distance = 3.0

        # Публикуем текущее расстояние
        msg = Float32()
        msg.data = self.distance
        self.distance_publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = DistanceSensor()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()