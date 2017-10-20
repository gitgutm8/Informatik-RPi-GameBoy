from collections import deque
from enum import Enum, auto
import RPi.GPIO as GPIO

# Hier die Stecker einfügen, die beim RPi verwendet werden sollen
CROSS_UP = 0
CROSS_LEFT = 1
CROSS_RIGHT = 2
CROSS_DOWN = 3
EXTRA_A = 4
EXTRA_B = 5

events = deque()


class EventType(Enum):
    BUTTON_UP = auto()
    BUTTON_DOWN = auto()


class _ButtonEvent:

    def __init__(self, type, **attrs):
        self.__dict__.update(**attrs)
        self._type = type

    def __eq__(self, value):
        return self._type == value


def init():
    GPIO.setmode(GPIO.BCM)
    buttons = [
        CROSS_UP,
        CROSS_LEFT,
        CROSS_RIGHT,
        CROSS_DOWN,
        EXTRA_A,
        EXTRA_B
    ]
    GPIO.setup(buttons, GPIO.IN, GPIO.PUD_UP)
    for button in buttons:
       GPIO.add_event_detect(
            button,
            GPIO.RISING,
            callback=lambda b=button: events.append(_ButtonEvent(EventType.BUTTON_DOWN), button=b)
        )
       GPIO.add_event_detect(
            button,
            GPIO.FALLING,
            callback=lambda b=button: events.append(_ButtonEvent(EventType.BUTTON_UP), button=b)
        )


def get_button_presses():
    while events:
        yield events.popleft()
