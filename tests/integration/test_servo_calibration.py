import unittest
import os
import select

from parameterized import parameterized

import bpy

COMMAND_LENGTH = 5


class TestServoCalibration(unittest.TestCase):
    def setUp(self):
        self.receiver, self.sender = os.openpty()
        self.ttyname = os.ttyname(self.sender)

    def tearDown(self):
        try:
            os.close(self.sender)
            os.close(self.receiver)
        except OSError:
            pass

        bpy.context.window_manager.servo_animation.position_jump_handling = False
        bpy.context.window_manager.servo_animation.transition_speed = 2
        bpy.context.object.data.bones['Bone'].servo_settings.position_min = 0
        bpy.context.object.data.bones['Bone'].servo_settings.position_max = 180
        bpy.context.scene.frame_set(1)

    def read_bytes(self):
        read_bytes = []

        while select.select([self.receiver], [], [], 0.1)[0]:
            chunk = os.read(self.receiver, 4096)
            if not chunk:
                break

            read_bytes.extend(bytes([value]) for value in chunk)

        return read_bytes

    @parameterized.expand([
        ("without handling", False, 45, 135, 4),
        ("with handling and no frame jump", True, 45, 135, 4),
        ("with handling and alternative values", True, 80, 110, 4),
    ])
    def test_calibration(self, _name, handling, position_min, position_max, commands):
        servo_settings = bpy.context.object.data.bones['Bone'].servo_settings

        bpy.context.window_manager.servo_animation.position_jump_handling = handling

        assert servo_settings.position_min == 0
        assert servo_settings.position_max == 180

        bpy.ops.servo_animation.start_live_mode(
            'EXEC_DEFAULT',
            method='SERIAL',
            serial_port=self.ttyname,
            serial_baud=115200
        )
        bpy.ops.servo_animation.calibrate(
            'EXEC_DEFAULT',
            position_min=position_min,
            position_max=position_max
        )
        bpy.ops.servo_animation.stop_live_mode('EXEC_DEFAULT')

        assert servo_settings.position_min == position_min
        assert servo_settings.position_max == position_max

        read_bytes = self.read_bytes()

        assert len(read_bytes) == commands * COMMAND_LENGTH
