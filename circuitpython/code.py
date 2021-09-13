import board
from collections import namedtuple
from digitalio import DigitalInOut, Direction, Pull
import adafruit_dotstar as dotstar
import neopixel
import supervisor
import time

######################### COMMMANDS ##############################
Event = namedtuple("Event", ("status", "output"))


# noinspection PyMethodMayBeStatic
class Commands(object):

    def __init__(self):
        self.__not_found = lambda x: print("Invalid command. See 'help' for usage.")
        self.__preamble = ""

    def __listen(self):
        # Process the serial interface for input.
        if supervisor.runtime.serial_bytes_available:
            args = input().strip().split()

            if len(args) > 0:
                # Get the base command from the list of arguments
                cmd = args.pop(0)
                # Lookup the received command.
                func = getattr(self, cmd, self.__not_found)
                # Execute the command and pass the rest as arguments
                try:
                    self.__response(func(*args))
                except TypeError:
                    self.__response(Event(False, "Insufficient arguments"))
                except Exception as err:
                    self.__response(Event(False, err))

        return None

    def __response(self, event: Event):
        """
        Handles the response message

        :param event:
        :return:
        """
        if event.status:
            print("{}OK: {}".format(self.__preamble, event.output))
        else:
            print("{}ERR: {}".format(self.__preamble, event.output))

    def help(self):
        cmd_list = [func for func in dir(Commands) if callable(getattr(Commands, func)) and not func.startswith("__")]
        return Event(True, "List of Commands\n{}".format(", ".join(cmd_list)))

    def alert(self, color):
        pulse(RED, 3, 0.1)
        return Event(True, "Alert color {}".format(color))

    def br_set(self, value):
        value = int(value) / 100
        new = set_brightness(value)

        return Event(True, "Set brightness: {:.0%}".format(new))

    def br_up(self, value):
        value = float(value) / 100
        new = set_brightness(brightness + value)

        return Event(True, "Increase brightness: +{:.0%} [{:.0%}]".format(value, new))

    def br_down(self, value):
        value = int(value) / 100
        new = set_brightness(brightness - value)

        return Event(True, "Decrease brightness: -{:.0%} [{:.0%}]".format(value, new))

    def off(self):
        set_brightness(0)
        return Event(True, "Set brightness: 0%")


######################### HELPERS ##############################
def clip(value, lower, upper):
    return lower if value < lower else upper if value > upper else value


def set_brightness(value):
    """
    Takes a percentage value and sets the brightness.

    :param value:
    :return bool:
    """
    global brightness
    new_brightness = clip(value, 0, MAX_BRIGHTNESS)

    # Set the device brightness
    brightness = new_brightness
    neopixels.brightness = new_brightness
    dot.brightness = new_brightness

    return new_brightness


# LED Animations
def color_chase(color, wait):
    for i in range(NUMPIXELS):
        neopixels[i] = color
        time.sleep(wait)
        neopixels.show()
    time.sleep(0.5)


def pulse(color, pulses, speed=0.5, step=10):
    """
    TODO: You left off here. It works, but slow af. Might be brightness function.
    TODO: Try setting the RGBW values
    :param color:
    :param pulses:
    :param speed:
    :param step:
    :return:
    """
    for i in range(NUMPIXELS):
        neopixels[i] = color
    neopixels.show()

    b = int(brightness * 100)
    for _ in range(pulses):
        for x in range(b, int(MAX_BRIGHTNESS * 100), step):
            print(x)
            set_brightness(x)
            time.sleep(speed)
        for x in range(int(MAX_BRIGHTNESS * 100), 0, (step * -1)):
            print(x)
            set_brightness(x)
            time.sleep(speed)
        for x in range(0, int(MAX_BRIGHTNESS * 100), step):
            print(x)
            set_brightness(x)
            time.sleep(speed)
    else:
        print(x)
        set_brightness(b)



def rainbow_cycle(wait):
    for j in range(255):
        for i in range(NUMPIXELS):
            rc_index = (i * 256 // NUMPIXELS) + j
            neopixels[i] = wheel(rc_index & 255)
        neopixels.show()
        time.sleep(wait)


def wheel(pos):
    """
    Helper to give us a nice color swirl. The colours are a transition r - g - b - back to r.

    :param pos: Input a value 0 to 255 to get a color value.
    :return tuple:
    """
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


RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)


######################### HARDWARE SETUP ##############################
# LEDs
brightness = 0.1
MAX_BRIGHTNESS = 0.5  # SAFETY: Prevent LEDs from burning out.
# One pixel connected internally
dot = dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=brightness)
dot[0] = (0, 0, 0)
# NeoPixel strip (of 30 LEDs) connected on D4
NUMPIXELS = 30
neopixels = neopixel.NeoPixel(board.D4, NUMPIXELS, brightness=brightness, auto_write=False)
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

######################### MAIN LOOP ##############################

# Initialize objects on first run
serial = Commands()
i = 0

while True:
    # Turn on the LED to show the loop has been entered.
    led.value = True

    # Listen for commands on the serial interface
    serial.__listen()

    if not mode_1.value:
        dot[0] = (255, 255, 255)

    if mode_2.value:
        # spin internal LED around! autoshow is on
        dot[0] = wheel(i & 255)

        # also make the neopixels swirl around
        for p in range(NUMPIXELS):
            idx = int((p * 256 / NUMPIXELS) + i)
            neopixels[p] = wheel(idx & 255)
        neopixels.show()

        i = (i+1) % 256  # run from 0 to 255
    #time.sleep(0.01) # make bigger to slow down