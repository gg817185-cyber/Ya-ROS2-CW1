#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist


class RobotController(Node):
    """
    Управляющий узел робота.
    Получает статус системы и публикует команду движения.
    """

    def __init__(self):
        super().__init__('robot_controller')

        # Начальные параметры
        self.robot_status = 'ALL OK'
        self.current_mode = ''

        # Subscriber для статуса робота
        self.status_subscriber = self.create_subscription(
            String,
            '/robot_status',
            self.status_callback,
            10
        )

        # Publisher для команд движения
        self.cmd_vel_publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        # Таймер 10 Hz (каждые 0.1 секунды)
        self.timer = self.create_timer(0.1, self.update_command)

        self.get_logger().info('Robot Controller started')

    def status_callback(self, msg):
        """
        Получаем текущий статус робота.
        """
        self.robot_status = msg.data

    def update_command(self):
        """
        Определение команды движения по текущему статусу.
        """
        cmd = Twist()

        if self.robot_status == 'ALL OK':
            cmd.linear.x = 0.3
            cmd.angular.z = 0.0
            new_mode = 'MOVING FORWARD'

        elif self.robot_status == 'WARNING: Low battery':
            cmd.linear.x = 0.1
            cmd.angular.z = 0.0
            new_mode = 'SLOW MOVING'

        elif self.robot_status == 'WARNING: Obstacle close':
            cmd.linear.x = 0.0
            cmd.angular.z = 0.5
            new_mode = 'TURNING IN PLACE'

        else:
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0
            new_mode = 'STOPPED'

        # Логируем только изменение режима
        if new_mode != self.current_mode:
            self.get_logger().info(
                f'Mode changed: {self.current_mode} -> {new_mode} '
                f'(status: {self.robot_status})'
            )
            self.current_mode = new_mode

        # Публикуем команду движения
        self.cmd_vel_publisher.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = RobotController()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()