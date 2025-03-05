try:
    import can
except ImportError as e:
    from machine import CAN
    from mks_servo_can.mks_enums import *
    from prn_ import prn
import time
import logging

from mks_servo_can import MksServo

SPEED = MksServo.MAX_SPEED
ACCEL = MksServo.MAX_ACCELERATION >> 2
uSTEPS = 255 >> 4  # 16  # 1  # subdivisions
REVOL = 50  # revolutions of the motor shaft

# Stock slcan firmware on Windows
try:
    bus = can.interface.Bus(interface="slcan", channel="COM3", bitrate=500000)
    notifier = can.Notifier(bus, [])
except:
    bus = CAN(0, tx=5, rx=4, mode=CAN.NORMAL, bitrate=500_000)
    notifier = None

#     def can_send_cb(message):
#         print(f"can_send_cb()")
#         print(type(message))
#         print(f"can_send_cb({message})")
#         pass
#
#     def can_recv_cb(message):
#         print(f"can_recv_cb()")
#         print(type(message))
#         print(f"can_recv_cb({message})")
#
#     #bus.irq_recv(can_recv_cb)
#     #bus.irq_send(can_send_cb)


def wait_for_motor_idle2(timeout=None):
    print("Speed:", servo.read_motor_speed(), end=" ", flush=True)
    start_time = time.perf_counter()
    while ((time.perf_counter() - start_time < timeout) if timeout else True) and servo.is_motor_running():
        print(servo.read_motor_speed(), end=" ", flush=True)
        time.sleep(0.1)  # Small sleep to prevent busy waiting
    print(servo.read_motor_speed(), flush=True)
    return servo.is_motor_running()


# @prn
def move_motor(absolute_position, timeout=None):
    print(f"\nMoving motor to absolute position {absolute_position}", flush=True)
    servo.run_motor_absolute_motion_by_axis(SPEED, ACCEL, absolute_position)
    is_motor_running = wait_for_motor_idle2(timeout)
    value = servo.read_encoder_value_addition()
    error = absolute_position - value
    print(f"Movement at {absolute_position} with error:{error}, is_motor_running:{is_motor_running} query_motor_status:{servo.query_motor_status()}", flush=True)
    time.sleep(0.5)


servo = MksServo(bus, notifier, 1)

# try:
#     print("emergency_stop_motor")
#     print(servo.emergency_stop_motor())
# except:
#     pass

# # print("set_slave_respond_active")
# # print(type(MksServo))
# print(type(MksServo.Enable))
# print(type(MksServo.Enable.Enable))
# # # print(dir(MksServo))
# print(dir(MksServo.Enable))
# print(dir(MksServo.Enable.Enable))
# print(servo.set_slave_respond_active(MksServo.Enable.Enable, MksServo.Enable.Enable))
# 1/0
print("Set subdivisions", uSTEPS)
print(servo.set_subdivisions(uSTEPS))
print("Set the subdivision interpolation")
print(servo.set_subdivision_interpolation(MksServo.Enable.Enable))

# print("Set work mode", MksServo.WorkMode.SrClose)
# print(servo.set_work_mode(MksServo.WorkMode.SrClose))
print("Set work mode", MksServo.WorkMode.SrvFoc)
print(servo.set_work_mode(MksServo.WorkMode.SrvFoc))

print("Set working current", 1000)
print(servo.set_working_current(1000))
print("Set current axis to zero")
print(servo.set_current_axis_to_zero())
# print("Calibrate encoder")
# print(servo.b_calibrate_encoder())

# print("Go home")
# print(servo.set_home(MksServo.EndStopLevel.High, MksServo.Direction.CW, 200, MksServo.Enable.Disable))
# print(servo.b_go_home())

print("servo.query_motor_status()")
print(servo.query_motor_status())

print("servo.is_motor_running()")
print(servo.is_motor_running())

print("servo.read_encoder_value_carry()")
print(servo.read_encoder_value_carry())
print("servo.read_encoder_value_addition()")
print(servo.read_encoder_value_addition())

print("Position 1")
print(servo.read_encoder_value_addition())

print("MOVING")
print(servo.run_motor_relative_motion_by_pulses(MksServo.Direction.CCW, 400, 1, 0x4000))
print(servo.wait_for_motor_idle())

print("Position 2")
print(servo.read_encoder_value_addition())
print(servo.run_motor_relative_motion_by_pulses(MksServo.Direction.CW, 400, 1, 0x4000 * 2))
print(servo.wait_for_motor_idle())

print("Position 3")
print(servo.read_encoder_value_addition())
print(servo.run_motor_relative_motion_by_pulses(MksServo.Direction.CCW, 400, 1, 0x4000))
print(servo.wait_for_motor_idle(10))
print("Stop motor relative motion by pulses")
print(servo.stop_motor_relative_motion_by_pulses(ACCEL))

print("Position 4")
print(servo.read_encoder_value_addition())

try:
    while True:
        move_motor(0x4000 * REVOL)
        move_motor(0)
        move_motor(-0x4000 * REVOL)
except KeyboardInterrupt:
    pass

print("Position 5")
print(servo.read_encoder_value_addition())

print("Stop motor absolute motion by axis")
print(servo.stop_motor_absolute_motion_by_axis(ACCEL))

try:
    notifier.stop()
except:
    pass
try:
    bus.shutdown()
except:
    bus.deinit()
