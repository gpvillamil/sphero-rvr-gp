import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import asyncio

from helper_keyboard_input import KeyboardHelper
from sphero_sdk import SerialAsyncDal
from sphero_sdk import SpheroRvrAsync

# initialize global variables
key_helper = KeyboardHelper()
current_key_code = -1
driving_keys = [ord('w'), ord('a'), ord('s'), ord('d'), ord(' ')]
max_speed = 255
max_heading = 359
speed = 0
heading = 0
flags = 0

loop = asyncio.get_event_loop()
rvr = SpheroRvrAsync(
    dal=SerialAsyncDal(
        loop
    )
)

def keycode_callback(keycode):
    global current_key_code
    current_key_code = keycode
    print("Key code updated: ", str(current_key_code))


async def main():
    """
    Runs the main control loop for this demo.  Uses the KeyboardHelper class to read a keypress from the terminal.

    W - Go forward.  Press multiple times to increase speed.
    A - Decrease heading by -10 degrees with each key press.
    S - Go reverse. Press multiple times to increase speed.
    D - Increase heading by +10 degrees with each key press.
    Spacebar - Reset speed and flags to 0. RVR will coast to a stop

    """
    global current_key_code
    global speed
    global heading
    global flags

    await rvr.wake()

    await rvr.reset_yaw()

    while True:

        if current_key_code == driving_keys[0]:  # W
            # if previously going reverse, reset speed back to 64
            if flags == 1:
                speed = 64
            else:
                # else increase speed
                speed += 64
            # go forward
            flags = 0
        elif current_key_code == driving_keys[1]:  # A
            heading -= 10
        elif current_key_code == driving_keys[2]:  # S
            # if previously going forward, reset speed back to 64
            if flags == 0:
                speed = 64
            else:
                # else increase speed
                speed += 64
            # go reverse
            flags = 1
        elif current_key_code == driving_keys[3]:  # D
            heading += 10
        elif current_key_code == driving_keys[4]:  # SPACE
            # reset speed and flags, but don't modify heading.
            speed = 0
            flags = 0

        # check the speed value, and wrap as necessary.
        if speed > max_speed:
            speed = max_speed
        elif speed < -max_speed:
            speed = -max_speed

        # check the heading value, and wrap as necessary.
        if heading > max_heading:
            heading = heading - max_heading
        elif heading < 0:
            heading = max_heading + heading

        # reset the key code every loop
        current_key_code = -1

        # issue the driving command
        await rvr.drive_with_heading(speed, heading, flags)

        # sleep the infinite loop for a 10th of a second to avoid flooding the serial port.
        await asyncio.sleep(0.1)


def run_loop():
    global loop
    global key_helper
    key_helper.set_callback(keycode_callback)
    loop.run_until_complete(
        asyncio.gather(
            main()
        )
    )


if __name__ == "__main__":
    loop.run_in_executor(None, key_helper.get_key_continuous)
    try:
        run_loop()
    except KeyboardInterrupt:
        print("Keyboard Interrupt...")
        key_helper.end_get_key_continuous()
    finally:
        print("Press any key to exit.")
        exit(1)
