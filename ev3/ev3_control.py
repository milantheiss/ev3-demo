#!/usr/bin/env python3

import logging
import threading
from time import sleep
from ev3dev2.motor import Motor, MoveJoystick
from ev3dev2.sound import Sound
from gamepad_util import Gamepad, GamepadHandler

logging.basicConfig(level=logging.DEBUG)

spkr = Sound()

test = GamepadHandler(Gamepad())

motors = MoveJoystick("outD", "outA")
motorD = Motor("outD")
motorA = Motor("outA")

playing_sound = False


def play_sound_file(filepath):
    global playing_sound

    def _play_sound(filepath):
        global playing_sound
        logging.info("Playing %s", filepath)
        spkr.play_file(wav_file=filepath, play_type=0)
        playing_sound = False

    if (playing_sound is False):
        playing_sound = True
        threading.Thread(target=_play_sound, args=(filepath,)).start()
    else:
        logging.error("Sound file will not be played: EV3 is already playing a sound file.")


def action_left_stick():
    if (motorA.speed != 0 or motorD.speed != 0):
        logging.info("Motor A %d Motor D %d", motorA.speed, motorD.speed)
    motors.on(test.limit_input_percentage(test.connected_gamepad.LEFT_STICK_X, 70),
              test.limit_input_percentage((test.connected_gamepad.LEFT_STICK_Y * -1), 70))


def _on_press_button_x():
    play_sound_file("sounds/doyouknowthewae.wav")


def main():
    logging.debug("Use Controller to start input handling")
    test.connected_gamepad.start_reading_inputs()
    while not test.connected_gamepad.checking_for_inputs:
        sleep(1)

    test.handle_onpress_events(onpress_button_x=_on_press_button_x)
    test.handle_stick_outputs(action_left_stick=action_left_stick)


if __name__ == '__main__':
    main()