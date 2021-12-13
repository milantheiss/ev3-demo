#!/usr/bin/env python3

import logging
from time import sleep
from ev3dev2.sensor.lego import GyroSensor

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s")
logger = logging.getLogger('PI CONTROLLER')
logger.setLevel(logging.DEBUG)


def get_rotation(rotation, changed_degrees):
    if changed_degrees < 0:
        changed_degrees = abs(changed_degrees)
        while changed_degrees > 360:
            changed_degrees -= 360
        if changed_degrees < rotation:
            return rotation - changed_degrees
        if changed_degrees > rotation:
            changed_degrees -= rotation
            return 360 - changed_degrees
    if changed_degrees > 0:
        while changed_degrees > 360:
            changed_degrees -= 360
        if changed_degrees <= (360 - rotation):
            return 0 if ((rotation + changed_degrees) == 360) else rotation + changed_degrees
        else:
            return changed_degrees - (360 - rotation)
    if changed_degrees == 0:
        return rotation


gyro_sensor = GyroSensor()

gyro_sensor.mode = GyroSensor.MODE_GYRO_ANG

gyro_sensor.reset()

rotation = 0

for i in range(0, 200):
    logger.info("Old rotation %s", rotation)
    logger.info("Rotatet %s Degrees", gyro_sensor.angle)
    rotation = get_rotation(rotation, gyro_sensor.angle)
    gyro_sensor.reset()
    logger.info("New Rotation %s", rotation)
    sleep(1)


def reset_rotation():
    rotation = 0
