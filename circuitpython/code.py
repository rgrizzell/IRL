import board
from digitalio import DigitalInOut, Direction, Pull
import adafruit_dotstar as dotstar
import neopixel
import supervisor
import time


######################### COMMMANDS ##############################

# noinspection PyMethodMayBeStatic
class Commands(object):

    def __init__(self):
        self.not_found = lambda x: print("Invalid command. See 'help' for usage.")

    def __listen(self):
        # Process the serial interface for input.
        if supervisor.runtime.serial_bytes_available:
            args = input().strip().split()

            if len(args) > 0:
                # Get the base command from the list of arguments
                cmd = args.pop(0)
                # Lookup the received command.
                func = getattr(self, cmd, self.not_found)
                # Execute the command and pass the rest as arguments
                func(*args)

        return None

    def __response(self, response):
        """
        TODO: Reverse engineer the AT Command protocol

        :param response:
        :return:
        """
        print(response)

    def help(self):
        cmd_list = [func for func in dir(Commands) if callable(getattr(Commands, func)) and not func.startswith("__")]
        print("List of Commands")
        print(", ".join(cmd_list))
        return True

    def alert(self, color):
        print("OK: Alert color {}".format(color))
        return True

    def br_set(self, value):
        set_brightness(float(value))
        print("OK: Set brightness: {}%".format(value))
        return True

    def br_up(self, value):
        print("OK: Increase brightness: +{}%".format(value))
        return True

    def br_down(self, value):
        print("OK: Decrease brightness: -{}%".format(value))
        return True


######################### HELPERS ##############################

# Helper to give us a nice color swirl
def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if (pos < 0) or (pos > 255):
        return (0, 0, 0)
    if pos < 85:
        return (int(255 - pos*3), int(pos*3), 0)
    elif pos < 170:
        pos -= 85
        return (0, int(255 - (pos*3)), int(pos*3))
    else:
        pos -= 170
        return (int(pos*3), 0, int(255 - pos*3))


def set_brightness(value):
    """
    Takes a percentage value and sets the brightness
    :param value:
    :return bool:
    """
    if 0 <= value <= 100:
        b = value/100
        neopixels.brightness = b
        dot.brightness = b
        return True
    else:
        return False


######################### HARDWARE SETUP ##############################

# One pixel connected internally!
dot = dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.1)
dot[0] = (0, 0, 0)

# Built in red LED
led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT

# Digital switch input
mode_1 = DigitalInOut(board.D1)
mode_1.direction = Direction.INPUT
mode_1.pull = Pull.UP
mode_2 = DigitalInOut(board.D2)
mode_2.direction = Direction.INPUT
mode_2.pull = Pull.UP

# NeoPixel strip (of 30 LEDs) connected on D4
NUMPIXELS = 30
neopixels = neopixel.NeoPixel(board.D4, NUMPIXELS, brightness=0.1, auto_write=False)

######################### MAIN LOOP ##############################

# Initialize objects on first run
serial = Commands()
i = 0

while True:
    # Turn on the LED to show the loop has been entered.
    led.value = True

    # Listen for commands on the serial interface
    serial.__listen()

    if mode_1.value:
        dot[0] = (255, 255, 255)

    if not mode_2.value:
        # spin internal LED around! autoshow is on
        dot[0] = wheel(i & 255)

        # also make the neopixels swirl around
        for p in range(NUMPIXELS):
            idx = int((p * 256 / NUMPIXELS) + i)
            neopixels[p] = wheel(idx & 255)
        neopixels.show()

        i = (i+1) % 256  # run from 0 to 255
    #time.sleep(0.01) # make bigger to slow down