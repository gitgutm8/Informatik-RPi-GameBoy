import math
import pygame as pg
from functools import wraps


class Timer:

    def __init__(self, interval, callback, once=False):
        self.interval = interval
        self.callback = callback
        self.time = 0
        self.once = once
        self.alive = True

    def update(self, dt):
        """
        Checks if it's time to execute the callback.

        :param dt: {int} time since last update in seconds
        :return: {None}
        """
        if not self.alive:
            return

        self.time += dt
        if self.time >= self.interval:
            self.time -= self.interval
            self.callback()

            if self.once:
                self.alive = False


def divide_sprite_sheet(sheet, width, height, sprite_width, sprite_height, sprites=None):
    """
    Divides a sprite sheet in evenly sized images so they can be used
    for an animation.

    :param sheet: {pygame.Surface} sprite sheet
    :param width: {int} height of the sheet in sprites
    :param height: {int} width of the sheet in sprites
    :param sprite_width: {int} width of each sprite in pixels
    :param sprite_height: {int} height of each sprite in pixels
    :param sprites: {int} number of sprites, only needed if the last row
                    of the sheet contains less sprites
    :return: {list<pygame.Surface>} the separated images
    """
    sprites = sprites or width * height
    sheet = pg.image.load(sheet).convert()
    images = []
    for y in range(0, height*sprite_height, sprite_height):
        for x in range(0, width*sprite_width, sprite_width):
            if sprites <= 0:
                return images

            rect = pg.Rect(x, y, sprite_width, sprite_height)
            image = pg.Surface(rect.size)
            image.blit(sheet, (0, 0), rect)
            image.set_colorkey((255, 0, 255))
            images.append(image)
            sprites -= 1
    return images


def require_state(state, bool_=True):
    """
    A decorator of second degree, that calls the decorated method only
    if the specified attribute of the object, that currently binds the
    method, has the same value as `_bool`.

    :param state: {str} attribute to be checked
    :param bool_: {bool} boolean value the attribute is checked against
    :return: {function} decorator
    """
    def dec(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            if getattr(self, state) == bool_:
                method(self, *args, **kwargs)
        return wrapper
    return dec


class Vector(tuple):

    def __add__(self, other):
        return Vector(v + w for v, w in zip(self, other))

    def __radd__(self, other):
        return Vector(v + w for v, w in zip(self, other))

    def __sub__(self, other):
        return Vector(v - w for v, w in zip(self, other))

    def __mul__(self, scalar):
        return Vector(v * scalar for v in self)

    def __rmul__(self, scalar):
        return Vector(v * scalar for v in self)

    def __truediv__(self, scalar):
        return Vector(v / scalar for v in self)

    def __floordiv__(self, scalar):
        return Vector(v // scalar for v in self)

    def __mod__(self, other):
        return Vector(v % w for v, w in zip(self, other))

    def __ceil__(self):
        return Vector(math.ceil(v) for v in self)

    def __neg__(self):
        return -1 * self

    def __round__(self, n=0):
        return Vector(round(v, n) for v in self)

    def __floor__(self):
        return Vector(math.floor(v) for v in self)

    def length(self):
        return sum(v**2 for v in self) ** 0.5

    def normalize(self):
        return self / self.length()

    def deflect_x(self):
        return Vector2(-self[0], self[1])

    def deflect_y(self):
        return Vector2(self[0], -self[1])


def Vector2(x_or_pair, y=None):
    """
    A wrapper around the `Vector` class.

    :param x_or_pair: {float/tuple<float>} x, y pair of vector coordinates or just the x coordinate
    :param y: {float} y coordinate, neede if first argument is just x
    :return: {Vector} a new 2-component vector
    """
    if y is None:
        return Vector(x_or_pair)
    return Vector((x_or_pair, y))

DIRECTION = {
    'UP': Vector2(0, -1),
    'RIGHT_UP': Vector2(1, -1).normalize(),
    'RIGHT': Vector2(1, 0),
    'RIGHT_DOWN': Vector2(1, 1).normalize(),
    'DOWN': Vector2(0, 1),
    'LEFT_DOWN': Vector2(-1, 1).normalize(),
    'LEFT': Vector2(-1, 0),
    'LEFT_UP': Vector2(-1, -1).normalize(),
    'NONE': Vector2(0, 0)
}
