try:
    import can
except ImportError as e:
    from machine import CAN
    from mks_servo_can.mks_enums import *
import time
import logging

from mks_servo_can import MksServo

REVOL = 150  # revolutions of the motor shaft

# Stock slcan firmware on Windows
try:
    bus = can.interface.Bus(interface="slcan", channel="COM3", bitrate=500000)
    notifier = can.Notifier(bus, [])
except:
    bus = CAN(0, tx=5, rx=4, mode=CAN.NORMAL, bitrate=500_000)
    notifier = None


def wait_for_motor_idle2(timeout=None):
    start_time = time.perf_counter()
    while ((time.perf_counter() - start_time < timeout) if timeout else True) and servo.is_motor_running():
        print(servo.read_motor_speed(), end=" ", flush=True)
        # time.sleep(0.1)  # Small sleep to prevent busy waiting
    print("ooo", servo.read_motor_speed(), flush=True)
    return servo.is_motor_running()


def move_motor(absolute_position, timeout=None):
    print(f"\nMoving motor to absolute position {absolute_position}", flush=True)
    print("Speed:", servo.read_motor_speed(), end=" ", flush=True)
    servo.run_motor_absolute_motion_by_axis(600, 0, absolute_position)
    is_motor_running = wait_for_motor_idle2(timeout)
    value = servo.read_encoder_value_addition()
    error = absolute_position - value
    print(f"Movement at {absolute_position} with error:{error}, is_motor_running:{is_motor_running}, query_motor_status:{servo.query_motor_status()}", flush=True)
    time.sleep(0.5)


servo = MksServo(bus, notifier, 1)

try:
    print("emergency_stop_motor")
    print(servo.emergency_stop_motor())
except:
    pass
print("set_slave_respond_active()")
print(servo.set_slave_respond_active(MksServo.Enable.Enable, MksServo.Enable.Disable))
print("servo.set_work_mode(MksServo.WorkMode.SrvFoc)")
print(servo.set_work_mode(MksServo.WorkMode.SrvFoc))
print("servo.set_subdivisions(16)")
print(servo.set_subdivisions(16))
print("servo.set_working_current(2000)")
print(servo.set_working_current(2000))
print("servo.set_current_axis_to_zero()")
print(servo.set_current_axis_to_zero())

try:
    while True:
        move_motor(0x4000 * REVOL)
        move_motor(0)
except KeyboardInterrupt:
    pass

notifier.stop()
bus.shutdown()
